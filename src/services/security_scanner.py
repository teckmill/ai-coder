from typing import Dict, List
import ast
import logging
from .base_service import BaseService

logger = logging.getLogger(__name__)

class SecurityScanner(BaseService):
    """Service for scanning code for security vulnerabilities."""
    
    COMMON_VULNERABILITIES = {
        "python": {
            "sql_injection": [
                "execute",
                "executemany",
                "raw",
                "cursor.execute"
            ],
            "command_injection": [
                "os.system",
                "subprocess.run",
                "subprocess.Popen",
                "eval",
                "exec"
            ],
            "insecure_deserialization": [
                "pickle.loads",
                "yaml.load",
                "eval",
                "literal_eval"
            ],
            "path_traversal": [
                "open(",
                "file(",
                "os.path",
                "pathlib"
            ],
            "weak_crypto": [
                "md5",
                "sha1",
                "random"
            ]
        }
    }
    
    def scan_code(self, code: str, language: str) -> Dict:
        """Scan code for security vulnerabilities."""
        try:
            # Get security analysis from LLM
            prompt = f"""
            Analyze this {language} code for security vulnerabilities including:
            1. Injection vulnerabilities
            2. Authentication issues
            3. Data exposure risks
            4. Security misconfigurations
            5. Known CVEs in dependencies
            
            Code to analyze:
            {code}
            
            Provide detailed security analysis and remediation steps.
            """
            
            response = self._get_llm_suggestions(prompt)
            
            # Perform static security analysis if Python
            vulnerabilities = []
            if language.lower() == "python":
                vulnerabilities = self._analyze_python_security(code)
            
            return {
                "vulnerabilities": vulnerabilities,
                "security_analysis": response.get("explanation", ""),
                "remediation_code": response.get("code", "")
            }
        except Exception as e:
            logger.error(f"Error in security scanning: {str(e)}", exc_info=True)
            raise
    
    def _analyze_python_security(self, code: str) -> List[Dict]:
        """Perform static security analysis on Python code."""
        try:
            tree = ast.parse(code)
            vulnerabilities = []
            
            vulnerabilities.extend(self._check_sql_injection(tree))
            vulnerabilities.extend(self._check_command_injection(tree))
            vulnerabilities.extend(self._check_insecure_deserialization(tree))
            vulnerabilities.extend(self._check_path_traversal(tree))
            vulnerabilities.extend(self._check_crypto(tree))
            vulnerabilities.extend(self._check_hardcoded_secrets(tree))
            
            return vulnerabilities
        except Exception as e:
            logger.error(f"Error in Python security analysis: {str(e)}", exc_info=True)
            return []
    
    def _check_sql_injection(self, tree: ast.AST) -> List[Dict]:
        """Check for potential SQL injection vulnerabilities."""
        vulnerabilities = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.COMMON_VULNERABILITIES["python"]["sql_injection"]:
                        vulnerabilities.append({
                            "type": "sql_injection",
                            "severity": "HIGH",
                            "line": node.lineno,
                            "message": "Potential SQL injection vulnerability detected",
                            "recommendation": "Use parameterized queries or an ORM"
                        })
        return vulnerabilities
    
    def _check_command_injection(self, tree: ast.AST) -> List[Dict]:
        """Check for potential command injection vulnerabilities."""
        vulnerabilities = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, (ast.Name, ast.Attribute)):
                    func_name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr
                    if func_name in self.COMMON_VULNERABILITIES["python"]["command_injection"]:
                        vulnerabilities.append({
                            "type": "command_injection",
                            "severity": "HIGH",
                            "line": node.lineno,
                            "message": "Potential command injection vulnerability detected",
                            "recommendation": "Use subprocess.run with shell=False and input validation"
                        })
        return vulnerabilities
    
    def _check_insecure_deserialization(self, tree: ast.AST) -> List[Dict]:
        """Check for insecure deserialization vulnerabilities."""
        vulnerabilities = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.COMMON_VULNERABILITIES["python"]["insecure_deserialization"]:
                        vulnerabilities.append({
                            "type": "insecure_deserialization",
                            "severity": "HIGH",
                            "line": node.lineno,
                            "message": "Insecure deserialization detected",
                            "recommendation": "Use safe alternatives like json.loads() or yaml.safe_load()"
                        })
        return vulnerabilities
    
    def _check_path_traversal(self, tree: ast.AST) -> List[Dict]:
        """Check for potential path traversal vulnerabilities."""
        vulnerabilities = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.COMMON_VULNERABILITIES["python"]["path_traversal"]:
                        vulnerabilities.append({
                            "type": "path_traversal",
                            "severity": "MEDIUM",
                            "line": node.lineno,
                            "message": "Potential path traversal vulnerability detected",
                            "recommendation": "Use os.path.abspath() and validate file paths"
                        })
        return vulnerabilities
    
    def _check_crypto(self, tree: ast.AST) -> List[Dict]:
        """Check for weak cryptographic practices."""
        vulnerabilities = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name in self.COMMON_VULNERABILITIES["python"]["weak_crypto"]:
                        vulnerabilities.append({
                            "type": "weak_crypto",
                            "severity": "MEDIUM",
                            "line": node.lineno,
                            "message": f"Use of weak cryptographic function: {name.name}",
                            "recommendation": "Use strong cryptographic functions from cryptography package"
                        })
        return vulnerabilities
    
    def _check_hardcoded_secrets(self, tree: ast.AST) -> List[Dict]:
        """Check for hardcoded secrets and credentials."""
        vulnerabilities = []
        secret_patterns = [
            "password",
            "secret",
            "api_key",
            "token",
            "credential"
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id.lower()
                        if any(pattern in name for pattern in secret_patterns):
                            if isinstance(node.value, ast.Str):
                                vulnerabilities.append({
                                    "type": "hardcoded_secret",
                                    "severity": "HIGH",
                                    "line": node.lineno,
                                    "message": "Hardcoded secret or credential detected",
                                    "recommendation": "Use environment variables or secure secret management"
                                })
        return vulnerabilities
