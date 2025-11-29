import ast
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class StaticAnalyzer:
    """Static code analyzer for Python files"""
  
    def __init__(self):
        self.issues = []
  
    def analyze_code(self, code: str, file_path: str = "") -> List[Dict[str, Any]]:
        """Analyze Python code for common issues"""
        self.issues = []
      
        try:
            tree = ast.parse(code)
            self._analyze_ast(tree, file_path)
        except SyntaxError as e:
            self.issues.append({
                'type': 'syntax_error',
                'message': f'Syntax error: {e}',
                'line': e.lineno,
                'severity': 'error',
                'file': file_path
            })
      
        return self.issues
  
    def _analyze_ast(self, tree: ast.AST, file_path: str):
        """Analyze AST for code issues"""
        visitors = [
            self._check_unused_imports,
            self._check_unused_variables,
            self._check_broad_exceptions,
            self._check_missing_returns,
            self._check_complex_functions
        ]
      
        for visitor in visitors:
            try:
                visitor(tree, file_path)
            except Exception as e:
                logger.warning(f"Error in analyzer {visitor.__name__}: {e}")
  
    def _check_unused_imports(self, tree: ast.AST, file_path: str):
        """Check for unused imports"""
        import_names = set()
        used_names = set()
      
        class ImportVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    import_names.add(alias.name.split('.')[0])
          
            def visit_ImportFrom(self, node):
                if node.module:
                    import_names.add(node.module.split('.')[0])
          
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
      
        visitor = ImportVisitor()
        visitor.visit(tree)
      
        unused_imports = import_names - used_names
        for imp in unused_imports:
            self.issues.append({
                'type': 'unused_import',
                'message': f'Unused import: {imp}',
                'severity': 'warning',
                'file': file_path
            })
  
    def _check_unused_variables(self, tree: ast.AST, file_path: str):
        """Check for unused variables (simplified)"""
        # This is a simplified version - full implementation would be more complex
        pass
  
    def _check_broad_exceptions(self, tree: ast.AST, file_path: str):
        """Check for broad exception handling"""
        class ExceptionVisitor(ast.NodeVisitor):
            def visit_ExceptHandler(self, node):
                if node.type is None:  # Bare except
                    self.issues.append({
                        'type': 'broad_exception',
                        'message': 'Avoid bare except clause',
                        'line': node.lineno,
                        'severity': 'warning',
                        'file': file_path
                    })
                elif isinstance(node.type, ast.Name) and node.type.id == 'Exception':
                    self.issues.append({
                        'type': 'broad_exception',
                        'message': 'Avoid catching generic Exception',
                        'line': node.lineno,
                        'severity': 'info',
                        'file': file_path
                    })
      
        visitor = ExceptionVisitor()
        visitor.issues = self.issues
        visitor.visit(tree)
  
    def _check_missing_returns(self, tree: ast.AST, file_path: str):
        """Check for functions that might be missing return statements"""
        class ReturnVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                returns_none = (
                    node.returns and
                    isinstance(node.returns, ast.Name) and
                    node.returns.id == 'None'
                )
              
                if not has_return and not returns_none:
                    # This is a heuristic - not all functions need returns
                    if len(node.body) > 3:  # Only warn for non-trivial functions
                        self.issues.append({
                            'type': 'possible_missing_return',
                            'message': f'Function {node.name} might need a return statement',
                            'line': node.lineno,
                            'severity': 'info',
                            'file': file_path
                        })
      
        visitor = ReturnVisitor()
        visitor.issues = self.issues
        visitor.visit(tree)
  
    def _check_complex_functions(self, tree: ast.AST, file_path: str):
        """Check for overly complex functions"""
        class ComplexityVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                complexity_score = self._calculate_complexity(node)
                if complexity_score > 10:  # Arbitrary threshold
                    self.issues.append({
                        'type': 'high_complexity',
                        'message': f'Function {node.name} might be too complex (score: {complexity_score})',
                        'line': node.lineno,
                        'severity': 'info',
                        'file': file_path
                    })
          
            def _calculate_complexity(self, node):
                """Calculate simple complexity score"""
                score = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                        score += 1
                    elif isinstance(child, ast.ExceptHandler):
                        score += 1
                return score
      
        visitor = ComplexityVisitor()
        visitor.issues = self.issues
        visitor.visit(tree)