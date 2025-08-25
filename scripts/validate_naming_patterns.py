#!/usr/bin/env python3
"""
Script para validar padrões de nomenclatura no projeto
Valida se todos os arquivos seguem o padrão contextId (camelCase)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def get_project_root() -> Path:
    """Retorna o diretório raiz do projeto"""
    current_file = Path(__file__)
    return current_file.parent.parent

def validate_naming_patterns() -> Dict[Path, Dict[str, int]]:
    """Valida se todos os arquivos seguem o padrão contextId"""
    
    project_root = get_project_root()
    
    # Padrões a procurar e suas prioridades
    patterns = {
        'contextId': r'\bcontextId\b',           # ✅ PADRÃO CORRETO
        'context_id': r'\bcontext_id\b',        # ❌ snake_case (migrar)
        'contextid': r'\bcontextid\b',          # ❌ lowercase (migrar)
        'context_Id': r'\bcontext_Id\b',        # ❌ mixed (migrar)
        'ContextId': r'\bContextId\b',          # ❌ PascalCase (migrar)
        'contextID': r'\bcontextID\b',          # ❌ mixed (migrar)
    }
    
    # Diretórios a verificar (Python files)
    dirs_to_check = ['service', 'state', 'components', 'pages', 'models']
    
    violations = {}
    total_files = 0
    files_with_violations = 0
    
    print("🔍 Validando padrões de nomenclatura...")
    print(f"📁 Diretório raiz: {project_root}")
    print("=" * 60)
    
    for directory in dirs_to_check:
        dir_path = project_root / directory
        if dir_path.exists():
            print(f"\n📂 Verificando diretório: {directory}")
            
            for file_path in dir_path.rglob('*.py'):
                total_files += 1
                file_violations = {}
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern_name, pattern in patterns.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            file_violations[pattern_name] = len(matches)
                    
                    if file_violations:
                        violations[file_path] = file_violations
                        files_with_violations += 1
                        
                except Exception as e:
                    print(f"⚠️  Erro ao ler {file_path}: {e}")
    
    return violations, total_files, files_with_violations

def generate_migration_report(violations: Dict[Path, Dict[str, int]]) -> str:
    """Gera relatório de migração"""
    
    if not violations:
        return "✅ Todos os arquivos seguem o padrão contextId!"
    
    report = []
    report.append("📊 RELATÓRIO DE VIOLAÇÕES")
    report.append("=" * 50)
    
    # Agrupar por tipo de violação
    violation_types = {}
    for file_path, patterns in violations.items():
        for pattern, count in patterns.items():
            if pattern not in violation_types:
                violation_types[pattern] = []
            violation_types[pattern].append((file_path, count))
    
    # Mostrar violações por tipo
    for pattern, files in violation_types.items():
        if pattern == 'contextId':
            continue  # Pular o padrão correto
        
        report.append(f"\n❌ {pattern.upper()} ({len(files)} arquivos):")
        total_count = sum(count for _, count in files)
        report.append(f"   Total de ocorrências: {total_count}")
        
        for file_path, count in files:
            relative_path = file_path.relative_to(get_project_root())
            report.append(f"   📁 {relative_path}: {count} ocorrências")
    
    # Resumo
    report.append("\n" + "=" * 50)
    report.append("📋 RESUMO")
    report.append(f"   Total de arquivos com violações: {len(violations)}")
    
    total_violations = sum(
        sum(patterns.values()) 
        for patterns in violations.values()
    )
    report.append(f"   Total de violações: {total_violations}")
    
    return "\n".join(report)

def suggest_migration_commands(violations: Dict[Path, Dict[str, int]]) -> str:
    """Sugere comandos de migração"""
    
    if not violations:
        return ""
    
    commands = []
    commands.append("\n🚀 COMANDOS DE MIGRAÇÃO SUGERIDOS")
    commands.append("=" * 50)
    
    # Comandos para cada arquivo
    for file_path in violations.keys():
        relative_path = file_path.relative_to(get_project_root())
        commands.append(f"\n# Migrar {relative_path}")
        commands.append(f"sed -i 's/context_id/contextId/g' {relative_path}")
        commands.append(f"sed -i 's/contextid/contextId/g' {relative_path}")
        commands.append(f"sed -i 's/context_Id/contextId/g' {relative_path}")
        commands.append(f"sed -i 's/ContextId/contextId/g' {relative_path}")
        commands.append(f"sed -i 's/contextID/contextId/g' {relative_path}")
    
    commands.append("\n# Verificar mudanças")
    commands.append("git diff")
    
    return "\n".join(commands)

def check_pydantic_aliases() -> List[Tuple[Path, str]]:
    """Verifica se os modelos Pydantic têm aliases corretos"""
    
    project_root = get_project_root()
    issues = []
    
    # Verificar service/types.py
    types_file = project_root / "service" / "types.py"
    if types_file.exists():
        try:
            with open(types_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar se Message tem contextId com alias
            if 'class Message' in content:
                if 'contextId' not in content:
                    issues.append((types_file, "Message não tem campo contextId"))
                elif 'alias=' not in content and 'context_id' in content:
                    issues.append((types_file, "Message deve usar alias para context_id"))
            
            # Verificar se MessageInfoFixed tem contextId
            if 'class MessageInfoFixed' in content:
                if 'contextId' not in content:
                    issues.append((types_file, "MessageInfoFixed não tem campo contextId"))
                    
        except Exception as e:
            issues.append((types_file, f"Erro ao ler arquivo: {e}"))
    
    return issues

def main():
    """Função principal"""
    
    print("🔍 VALIDADOR DE PADRÕES DE NOMENCLATURA")
    print("=" * 60)
    
    # Validar padrões
    violations, total_files, files_with_violations = validate_naming_patterns()
    
    # Verificar aliases Pydantic
    pydantic_issues = check_pydantic_aliases()
    
    # Gerar relatório
    print(f"\n📊 ESTATÍSTICAS")
    print(f"   Total de arquivos Python: {total_files}")
    print(f"   Arquivos com violações: {files_with_violations}")
    print(f"   Arquivos sem violações: {total_files - files_with_violations}")
    
    # Mostrar relatório de violações
    migration_report = generate_migration_report(violations)
    print(f"\n{migration_report}")
    
    # Mostrar problemas de Pydantic
    if pydantic_issues:
        print("\n⚠️  PROBLEMAS IDENTIFICADOS NO PYDANTIC")
        print("=" * 50)
        for file_path, issue in pydantic_issues:
            relative_path = file_path.relative_to(get_project_root())
            print(f"📁 {relative_path}: {issue}")
    
    # Sugerir comandos de migração
    if violations:
        migration_commands = suggest_migration_commands(violations)
        print(migration_commands)
        
        print("\n💡 RECOMENDAÇÕES")
        print("=" * 50)
        print("1. Execute os comandos de migração sugeridos")
        print("2. Verifique se os testes ainda passam")
        print("3. Adicione aliases Pydantic onde necessário")
        print("4. Execute este script novamente para validação")
    
    else:
        print("\n🎉 PARABÉNS! Todos os arquivos seguem o padrão!")
        print("✅ O projeto está pronto para integração com A2A Protocol e Google ADK")

if __name__ == "__main__":
    main()
