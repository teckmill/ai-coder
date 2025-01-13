"""Custom AI Coder model implementation."""

import torch
import torch.nn as nn
from transformers import PretrainedConfig, PreTrainedModel


class AiCoderConfig(PretrainedConfig):
    """Configuration class for AI Coder model."""

    model_type = "ai-coder-v1"

    def __init__(
        self,
        vocab_size=100000,
        hidden_size=8192,
        num_hidden_layers=80,
        num_attention_heads=64,
        intermediate_size=32768,
        hidden_act="swiglu",
        hidden_dropout_prob=0.1,
        attention_probs_dropout_prob=0.1,
        max_position_embeddings=32768,
        type_vocab_size=2,
        initializer_range=0.02,
        layer_norm_eps=1e-5,
        pad_token_id=0,
        bos_token_id=1,
        eos_token_id=2,
        **kwargs,
    ):
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps


class AiCoderAttention(nn.Module):
    """Multi-head attention with sliding window and flash attention."""

    def __init__(self, config):
        super().__init__()
        self.num_attention_heads = config.num_attention_heads
        self.hidden_size = config.hidden_size
        self.attention_head_size = config.hidden_size // config.num_attention_heads
        self.all_head_size = self.num_attention_heads * self.attention_head_size

        self.query = nn.Linear(config.hidden_size, self.all_head_size)
        self.key = nn.Linear(config.hidden_size, self.all_head_size)
        self.value = nn.Linear(config.hidden_size, self.all_head_size)
        self.dropout = nn.Dropout(config.attention_probs_dropout_prob)

        self.sliding_window = 4096
        self.use_flash_attention = True if torch.cuda.is_available() else False

    def transpose_for_scores(self, x):
        new_x_shape = x.size()[:-1] + (
            self.num_attention_heads,
            self.attention_head_size,
        )
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)

    def forward(self, hidden_states, attention_mask=None):
        query_layer = self.transpose_for_scores(self.query(hidden_states))
        key_layer = self.transpose_for_scores(self.key(hidden_states))
        value_layer = self.transpose_for_scores(self.value(hidden_states))

        if self.use_flash_attention:
            # Use flash attention if available
            attention_scores = torch.nn.functional.scaled_dot_product_attention(
                query_layer,
                key_layer,
                value_layer,
                attn_mask=attention_mask,
                dropout_p=self.dropout.p if self.training else 0.0,
                is_causal=True,
            )
        else:
            # Regular attention with sliding window
            attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
            attention_scores = attention_scores / torch.sqrt(
                torch.tensor(self.attention_head_size, dtype=torch.float32)
            )

            if attention_mask is not None:
                attention_scores = attention_scores + attention_mask

            # Apply sliding window
            window_mask = torch.ones_like(attention_scores)
            window_mask = torch.triu(window_mask, diagonal=self.sliding_window) + torch.tril(
                window_mask, diagonal=-self.sliding_window
            )
            attention_scores = attention_scores.masked_fill(window_mask == 1, float("-inf"))

            attention_probs = nn.functional.softmax(attention_scores, dim=-1)
            attention_probs = self.dropout(attention_probs)
            attention_scores = torch.matmul(attention_probs, value_layer)

        attention_scores = attention_scores.permute(0, 2, 1, 3).contiguous()
        new_shape = attention_scores.size()[:-2] + (self.all_head_size,)
        return attention_scores.view(*new_shape)


class AiCoderLayer(nn.Module):
    """Transformer layer with optimizations."""

    def __init__(self, config):
        super().__init__()
        self.attention = AiCoderAttention(config)
        self.intermediate = nn.Sequential(
            nn.Linear(config.hidden_size, config.intermediate_size),
            nn.SwiGLU() if config.hidden_act == "swiglu" else nn.GELU(),
        )
        self.output = nn.Linear(config.intermediate_size, config.hidden_size)
        self.layernorm1 = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.layernorm2 = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

    def forward(self, hidden_states, attention_mask=None):
        attention_output = self.attention(self.layernorm1(hidden_states), attention_mask)
        hidden_states = hidden_states + self.dropout(attention_output)

        layer_output = self.layernorm2(hidden_states)
        layer_output = self.intermediate(layer_output)
        layer_output = self.output(layer_output)

        return hidden_states + self.dropout(layer_output)


class AiCoderModel(PreTrainedModel):
    """Main AI Coder model implementation."""

    config_class = AiCoderConfig
    base_model_prefix = "ai_coder"

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def __init__(self, config):
        super().__init__(config)
        self.embeddings = nn.ModuleDict(
            {
                "word_embeddings": nn.Embedding(
                    config.vocab_size,
                    config.hidden_size,
                    padding_idx=config.pad_token_id,
                ),
                "position_embeddings": nn.Embedding(config.max_position_embeddings, config.hidden_size),
                "token_type_embeddings": nn.Embedding(config.type_vocab_size, config.hidden_size),
            }
        )
        self.layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)

        # Initialize transformer layers
        self.layers = nn.ModuleList([AiCoderLayer(config) for _ in range(config.num_hidden_layers)])

        # Initialize the weights
        self.apply(self._init_weights)

        # Enable gradient checkpointing if needed
        self.gradient_checkpointing = False

    def get_input_embeddings(self):
        return self.embeddings["word_embeddings"]

    def set_input_embeddings(self, value):
        self.embeddings["word_embeddings"] = value

    def forward(self, input_ids=None, attention_mask=None, token_type_ids=None, position_ids=None, **kwargs):
        input_shape = input_ids.size()
        batch_size, seq_length = input_shape

        if attention_mask is None:
            attention_mask = torch.ones(input_shape, device=input_ids.device)
        if token_type_ids is None:
            token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=input_ids.device)
        if position_ids is None:
            position_ids = torch.arange(seq_length, dtype=torch.long, device=input_ids.device)
            position_ids = position_ids.unsqueeze(0).expand(input_shape)

        # Get embeddings
        inputs_embeds = self.embeddings["word_embeddings"](input_ids)
        position_embeddings = self.embeddings["position_embeddings"](position_ids)
        token_type_embeddings = self.embeddings["token_type_embeddings"](token_type_ids)

        # Combine embeddings
        embeddings = inputs_embeds + position_embeddings + token_type_embeddings
        embeddings = self.layernorm(embeddings)
        embeddings = self.dropout(embeddings)

        # Prepare attention mask
        extended_attention_mask = attention_mask.unsqueeze(1).unsqueeze(2)
        extended_attention_mask = extended_attention_mask.to(dtype=self.dtype)
        extended_attention_mask = (1.0 - extended_attention_mask) * torch.finfo(self.dtype).min

        # Process through layers
        hidden_states = embeddings
        for layer in self.layers:
            if self.gradient_checkpointing and self.training:
                layer_outputs = torch.utils.checkpoint.checkpoint(layer, hidden_states, extended_attention_mask)
            else:
                layer_outputs = layer(hidden_states, extended_attention_mask)
            hidden_states = layer_outputs

        return hidden_states


class AiCoderForCausalLM(PreTrainedModel):
    """AI Coder model with language modeling head."""

    config_class = AiCoderConfig
    base_model_prefix = "ai_coder"

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def __init__(self, config):
        super().__init__(config)
        self.ai_coder = AiCoderModel(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

        # Initialize weights and apply final processing
        self.apply(self._init_weights)

        # Tie weights if configured
        if config.tie_word_embeddings:
            self.lm_head.weight = self.ai_coder.get_input_embeddings().weight

    def get_output_embeddings(self):
        return self.lm_head

    def set_output_embeddings(self, new_embeddings):
        self.lm_head = new_embeddings

    def forward(
        self, input_ids=None, attention_mask=None, token_type_ids=None, position_ids=None, labels=None, **kwargs
    ):
        hidden_states = self.ai_coder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            **kwargs,
        )

        lm_logits = self.lm_head(hidden_states)

        loss = None
        if labels is not None:
            # Shift so that tokens < n predict n
            shift_logits = lm_logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()

            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))

        return {"loss": loss, "logits": lm_logits} if loss is not None else lm_logits
