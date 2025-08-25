#!/usr/bin/env python3
"""
Script de refatoração automatizada para migrar nomes conflitantes.
Mapeia e substitui todos os campos com potencial de conflito.
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import argparse
import json
from datetime import datetime
import shutil


class NameRefactorer:
    """Refatora nomes ambíguos para nomes únicos e descritivos"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_made = []
        self.files_modified = set()
        
        # Mapeamento completo de nomes antigos para novos
        self.field_mapping = {
            # Variações de message_id
            r'\bmessage_id\b': 'unit_ref',
            r'\bmessageId\b': 'unit_ref',
            r'\bmessage_Id\b': 'unit_ref',
            r'\bMessageId\b': 'unit_ref',
            r'\bmessageid\b': 'unit_ref',
            
            # Variações de user_id
            r'\buser_id\b': 'author_tag',
            r'\buserId\b': 'author_tag',
            r'\buser_Id\b': 'author_tag',
            r'\bUserID\b': 'author_tag',
            
            # Content/text
            r'\bcontent\b': 'dialogue_body',
            r'\btext\b': 'dialogue_body',
            r'\bmessage_text\b': 'dialogue_body',
            r'\bmessage_content\b': 'dialogue_body',
            
            # Timestamps
            r'\btimestamp\b': 'creation_epoch',
            r'\bcreated_at\b': 'creation_epoch',
            r'\bupdated_at\b': 'last_activity_epoch',
            r'\bcreatedAt\b': 'creation_epoch',
            r'\bupdatedAt\b': 'last_activity_epoch',
            
            # Conversation/thread
            r'\bconversation_id\b': 'stream_ref',
            r'\bconversationId\b': 'stream_ref',
            r'\bconversationid\b': 'stream_ref',
            r'\bthread_id\b': 'stream_ref',
            r'\bthreadId\b': 'stream_ref',
            
            # Collections
            r'\bmessages\b': 'dialogue_units',
            r'\bconversations\b': 'conversation_streams',
            r'\bthreads\b': 'conversation_streams',
            
            # Task
            r'\btask_id\b': 'task_ref',
            r'\btaskId\b': 'task_ref',
            r'\btask_ids\b': 'task_refs',
            r'\btaskids\b': 'task_refs',
            
            # Event
            r'\bevent_id\b': 'event_ref',
            r'\beventId\b': 'event_ref',
            r'\bevent_type\b': 'event_category',
            
            # JSON-RPC
            r'\bmethod\b': 'operation_name',
            r'\bparams\b': 'operation_params',
            r'\bresult\b': 'operation_result',
            r'\berror\b': 'operation_error',
            
            # Boolean flags
            r'\bisactive\b': 'active_flag',
            r'\bisActive\b': 'active_flag',
            r'\bis_active\b': 'active_flag',
            
            # Generic names
            r'\bname\b': 'display_label',
            r'\btitle\b': 'stream_title',
            r'\bdescription\b': 'item_description',
            
            # Actor/user
            r'\bactor\b': 'actor_tag',
            r'\buser\b': 'participant_tag',
            r'\bagent\b': 'participant_tag',
            
            # Context
            r'\bcontext_id\b': 'context_ref',
            r'\bcontextId\b': 'context_ref',
            r'\bcontextid\b': 'context_ref',
        }
        
        # Mapeamento de tipos/classes
        self.type_mapping = {
            r'\bMessage\b': 'DialogueUnit',
            r'\bConversation\b': 'ConversationStream',
            r'\bThread\b': 'ConversationStream',
            r'\bChat\b': 'ConversationStream',
            r'\bUser\b': 'ParticipantProfile',
            r'\bAgent\b': 'ParticipantProfile',
            r'\bTask\b': 'TaskUnit',
            r'\bEvent\b': 'EventRecord',
            r'\bDelivery\b': 'TransmissionRecord',
        }
        
        # Imports que precisam ser atualizados
        self.import_mapping = {
            'from a2a.types import Message': 'from models.refactored_types import DialogueUnit',
            'from service.types import Message': 'from models.refactored_types import DialogueUnit',
            'Message': 'DialogueUnit',
            'Conversation': 'ConversationStream',
            'Event': 'EventRecord',
            'Task': 'TaskUnit',
        }

    def analyze_file(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Analisa um arquivo e identifica mudanças necessárias"""
        changes = []
        
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Verificar campos
                for old_pattern, new_name in self.field_mapping.items():
                    if re.search(old_pattern, line):
                        changes.append((line_num, old_pattern, new_name))
                
                # Verificar tipos
                for old_type, new_type in self.type_mapping.items():
                    if re.search(old_type, line):
                        changes.append((line_num, old_type, new_type))
        
        except Exception as e:
            print(f"❌ Erro ao analisar {file_path}: {e}")
        
        return changes

    def refactor_file(self, file_path: Path) -> bool:
        """Refatora um arquivo Python"""
        try:
            content = file_path.read_text()
            original = content
            
            # Aplicar mapeamento de campos
            for old_pattern, new_name in self.field_mapping.items():
                content = re.sub(old_pattern, new_name, content)
            
            # Aplicar mapeamento de tipos
            for old_type, new_type in self.type_mapping.items():
                content = re.sub(old_type, new_type, content)
            
            # Aplicar mapeamento de imports
            for old_import, new_import in self.import_mapping.items():
                content = content.replace(old_import, new_import)
            
            if content != original:
                if not self.dry_run:
                    # Fazer backup
                    backup_path = file_path.with_suffix(f'.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                    shutil.copy2(file_path, backup_path)
                    
                    # Escrever mudanças
                    file_path.write_text(content)
                    print(f"✅ Refatorado: {file_path}")
                    print(f"   Backup em: {backup_path}")
                else:
                    print(f"🔍 [DRY RUN] Mudanças detectadas em: {file_path}")
                
                self.files_modified.add(str(file_path))
                
                # Registrar mudanças
                changes = self.analyze_file(file_path)
                self.changes_made.extend([(str(file_path), c) for c in changes])
                
                return True
            else:
                print(f"⏭️  Sem mudanças: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao refatorar {file_path}: {e}")
            return False

    def refactor_project(self, root_dir: Path, exclude_dirs: Optional[List[str]] = None):
        """Refatora todos os arquivos Python no projeto"""
        exclude_dirs = exclude_dirs or ['venv', '.venv', '__pycache__', '.git', 'node_modules']
        
        # Encontrar todos os arquivos Python
        python_files = []
        for py_file in root_dir.glob("**/*.py"):
            # Pular diretórios excluídos
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue
            python_files.append(py_file)
        
        print(f"\n🔍 Encontrados {len(python_files)} arquivos Python")
        print(f"📁 Diretório raiz: {root_dir}")
        print(f"🚫 Excluindo: {', '.join(exclude_dirs)}")
        
        if self.dry_run:
            print("\n⚠️  MODO DRY RUN - Nenhuma mudança será salva\n")
        
        # Refatorar cada arquivo
        for py_file in python_files:
            self.refactor_file(py_file)
        
        # Relatório final
        self.print_report()

    def print_report(self):
        """Imprime relatório das mudanças"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE REFATORAÇÃO")
        print("="*60)
        
        if self.dry_run:
            print("⚠️  MODO DRY RUN - Nenhuma mudança foi salva")
        
        print(f"\n📁 Arquivos modificados: {len(self.files_modified)}")
        
        if self.files_modified:
            print("\nArquivos:")
            for file in sorted(self.files_modified):
                print(f"  • {file}")
        
        # Estatísticas de mudanças
        if self.changes_made:
            print(f"\n🔄 Total de mudanças potenciais: {len(self.changes_made)}")
            
            # Contar por tipo
            field_changes = sum(1 for _, (_, pattern, _) in self.changes_made 
                              if pattern in self.field_mapping)
            type_changes = sum(1 for _, (_, pattern, _) in self.changes_made 
                             if pattern in self.type_mapping)
            
            print(f"  • Campos renomeados: {field_changes}")
            print(f"  • Tipos atualizados: {type_changes}")
        
        print("\n✨ Refatoração completa!")

    def generate_migration_guide(self, output_path: Path):
        """Gera um guia de migração em markdown"""
        guide = []
        guide.append("# Guia de Migração - Nomenclatura Refatorada\n")
        guide.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        guide.append("\n## Mapeamento de Campos\n")
        guide.append("| Nome Antigo | Nome Novo | Descrição |\n")
        guide.append("|-------------|-----------|-----------|")
        
        for old, new in sorted(self.field_mapping.items()):
            old_clean = old.replace(r'\b', '').replace('\\', '')
            guide.append(f"| `{old_clean}` | `{new}` | Campo refatorado |")
        
        guide.append("\n## Mapeamento de Tipos\n")
        guide.append("| Tipo Antigo | Tipo Novo | Descrição |\n")
        guide.append("|------------|-----------|-----------|")
        
        for old, new in sorted(self.type_mapping.items()):
            old_clean = old.replace(r'\b', '').replace('\\', '')
            guide.append(f"| `{old_clean}` | `{new}` | Classe refatorada |")
        
        guide.append("\n## Arquivos Modificados\n")
        for file in sorted(self.files_modified):
            guide.append(f"- {file}")
        
        output_path.write_text('\n'.join(guide))
        print(f"\n📝 Guia de migração salvo em: {output_path}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Refatora nomes conflitantes no projeto'
    )
    parser.add_argument(
        'path',
        type=Path,
        nargs='?',
        default=Path.cwd(),
        help='Caminho do projeto (padrão: diretório atual)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simula as mudanças sem salvar'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        help='Diretórios a excluir',
        default=['venv', '.venv', '__pycache__', '.git', 'node_modules']
    )
    parser.add_argument(
        '--guide',
        type=Path,
        help='Caminho para salvar o guia de migração'
    )
    
    args = parser.parse_args()
    
    # Criar refatorador
    refactorer = NameRefactorer(dry_run=args.dry_run)
    
    # Executar refatoração
    refactorer.refactor_project(args.path, args.exclude)
    
    # Gerar guia se solicitado
    if args.guide:
        refactorer.generate_migration_guide(args.guide)


if __name__ == "__main__":
    main()