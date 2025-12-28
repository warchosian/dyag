"""
Générateurs de datasets pour fine-tuning.

Support:
- Rule-based generation (patterns regex)
- LLM-based generation
- Data augmentation
"""

import json
import random
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict


class DatasetGenerator(ABC):
    """Classe de base pour les générateurs de datasets."""

    @abstractmethod
    def generate(self, input_file: str, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Génère un dataset.

        Args:
            input_file: Fichier source (JSONL ou Markdown)
            count: Nombre d'exemples à générer
            **kwargs: Arguments additionnels spécifiques au générateur

        Returns:
            Liste de dictionnaires au format training (messages)
        """
        pass

    def load_chunks(self, file_path: str) -> List[Dict]:
        """Charge les chunks depuis un fichier JSONL."""
        chunks = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        return chunks

    def save_dataset(self, dataset: List[Dict], output_file: str) -> None:
        """Sauvegarde le dataset au format JSONL."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in dataset:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')


class RuleBasedGenerator(DatasetGenerator):
    """
    Générateur basé sur des règles/patterns regex.

    Extrait des informations structurées depuis les chunks et génère
    des Q&A avec des templates prédéfinis.

    Inspiré de: scripts/generate_training_from_mygusi.py
    """

    SYSTEM_PROMPT = """Tu es un assistant spécialisé dans les applications du système d'information.
Tu réponds aux questions de manière précise, détaillée et professionnelle.
Tu te bases uniquement sur les informations factuelles disponibles.
Tu cites toujours tes sources en indiquant les IDs des chunks utilisés."""

    def extract_hebergement(self, content: str) -> Optional[str]:
        """Extrait l'information d'hébergement."""
        match = re.search(r'Data center:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        match = re.search(r'Hébergement[^:]*:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def extract_technologie(self, content: str) -> List[str]:
        """Extrait les technologies."""
        technologies = []
        match = re.search(r'Technologie principale:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            technologies.append(match.group(1).strip())
        matches = re.findall(r'Technologie:\s*([^\n]+)', content, re.IGNORECASE)
        technologies.extend([m.strip() for m in matches])
        return list(set(technologies))

    def extract_domaine(self, content: str) -> Optional[str]:
        """Extrait le domaine métier."""
        match = re.search(r'Domaine métier:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            domaine = match.group(1).strip()
            if domaine and domaine != "***TEMPORAIRE***":
                return domaine
        return None

    def extract_description(self, content: str) -> Optional[str]:
        """Extrait la description."""
        match = re.search(r'Descriptif:\s*(.+?)(?=\n-|\n#|$)', content, re.IGNORECASE | re.DOTALL)
        if match:
            desc = match.group(1).strip()
            desc = re.sub(r'^\d+\.\s*', '', desc, flags=re.MULTILINE)
            return desc[:500]
        return None

    def extract_acteur_moa(self, content: str) -> Optional[str]:
        """Extrait l'acteur MOA."""
        match = re.search(r'Rôle d\'acteur:\s*MOA[^\n]*\n[^:]*Acteur:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def generate_qa_pairs(self, chunks: List[Dict]) -> List[Dict]:
        """Génère des paires Q&A depuis les chunks."""
        qa_pairs = []

        # Grouper par application
        apps = {}
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            app_id = metadata.get('id')
            app_name = metadata.get('nom')

            if not app_id or not app_name:
                continue

            if app_id not in apps:
                apps[app_id] = {'nom': app_name, 'chunks': []}
            apps[app_id]['chunks'].append(chunk)

        # Générer Q&A pour chaque application
        for app_id, app_data in apps.items():
            app_name = app_data['nom']
            all_content = '\n'.join([c.get('content', '') for c in app_data['chunks']])

            # Hébergement
            hebergement = self.extract_hebergement(all_content)
            if hebergement:
                qa_pairs.append({
                    'question': f"Qui héberge {app_name} ?",
                    'answer': f"{app_name} est hébergé par {hebergement}. [Source: chunk_{app_id}]",
                    'app_name': app_name,
                    'type': 'hebergement'
                })

            # Technologies
            technologies = self.extract_technologie(all_content)
            if technologies:
                tech_str = ', '.join(technologies[:3])
                qa_pairs.append({
                    'question': f"Quelles technologies utilise {app_name} ?",
                    'answer': f"{app_name} utilise les technologies suivantes : {tech_str}. [Source: chunk_{app_id}]",
                    'app_name': app_name,
                    'type': 'technologie'
                })

            # Domaine
            domaine = self.extract_domaine(all_content)
            if domaine:
                qa_pairs.append({
                    'question': f"Quel est le domaine métier de {app_name} ?",
                    'answer': f"{app_name} appartient au domaine métier : {domaine}. [Source: chunk_{app_id}]",
                    'app_name': app_name,
                    'type': 'domaine'
                })

            # Description
            description = self.extract_description(all_content)
            if description:
                qa_pairs.append({
                    'question': f"À quoi sert {app_name} ?",
                    'answer': f"{app_name} : {description} [Source: chunk_{app_id}]",
                    'app_name': app_name,
                    'type': 'description'
                })

            # MOA
            moa = self.extract_acteur_moa(all_content)
            if moa:
                qa_pairs.append({
                    'question': f"Qui est la MOA de {app_name} ?",
                    'answer': f"La maîtrise d'ouvrage (MOA) de {app_name} est assurée par {moa}. [Source: chunk_{app_id}]",
                    'app_name': app_name,
                    'type': 'moa'
                })

        return qa_pairs

    def generate(self, input_file: str, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Génère des exemples avec des patterns prédéfinis.

        Args:
            input_file: Fichier JSONL de chunks
            count: Nombre d'exemples à générer
            **kwargs: seed (pour reproductibilité)

        Returns:
            Liste d'exemples au format training
        """
        seed = kwargs.get('seed', 42)
        random.seed(seed)

        # Charger chunks
        chunks = self.load_chunks(input_file)

        # Générer Q&A
        qa_pairs = self.generate_qa_pairs(chunks)

        # Mélanger et limiter
        random.shuffle(qa_pairs)
        selected = qa_pairs[:count]

        # Convertir au format training
        examples = []
        for qa in selected:
            example = {
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": qa['question']},
                    {"role": "assistant", "content": qa['answer']}
                ]
            }
            examples.append(example)

        return examples


class LLMBasedGenerator(DatasetGenerator):
    """
    Générateur utilisant un LLM pour créer les réponses.

    Utilise GPT-4o-mini (ou autre LLM) pour générer des réponses
    de haute qualité depuis les chunks.

    Inspiré de: scripts/prepare_finetuning_data.py
    """

    SYSTEM_PROMPT = """Tu es un assistant spécialisé dans les applications du système d'information.
Tu réponds aux questions de manière précise, détaillée et professionnelle.
Tu te bases uniquement sur les informations factuelles disponibles.
Tu cites toujours tes sources en indiquant les IDs des chunks utilisés."""

    QUESTION_TEMPLATES = {
        'hébergeur': [
            "Qui héberge {app_name} ?",
            "Où est hébergée l'application {app_name} ?",
            "Quel est l'hébergeur de {app_name} ?",
            "Sur quelle plateforme est hébergé {app_name} ?",
        ],
        'technologies': [
            "Quelles technologies utilise {app_name} ?",
            "Quel est le stack technique de {app_name} ?",
            "Avec quoi est développé {app_name} ?",
            "Quels langages/frameworks sont utilisés pour {app_name} ?",
        ],
        'description': [
            "Qu'est-ce que {app_name} ?",
            "Quelle est la description de {app_name} ?",
            "À quoi sert {app_name} ?",
            "Peux-tu me présenter l'application {app_name} ?",
        ],
        'general': [
            "Donne-moi les informations sur {app_name}",
            "Présente-moi l'application {app_name}",
            "Que sais-tu sur {app_name} ?",
        ]
    }

    def generate_qa_from_chunk(self, chunk: Dict, llm_provider, question_type: Optional[str] = None) -> Optional[Dict]:
        """Génère une Q&A depuis un chunk avec un LLM."""
        app_name = chunk.get('metadata', {}).get('nom', 'Application')
        content = chunk.get('content', '')
        chunk_id = chunk.get('id', 'unknown')

        # Choisir un type de question aléatoire si non spécifié
        if question_type is None:
            question_type = random.choice(list(self.QUESTION_TEMPLATES.keys()))

        # Générer la question
        template = random.choice(self.QUESTION_TEMPLATES[question_type])
        question = template.format(app_name=app_name)

        # Générer la réponse avec le LLM
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""Contexte:
{content}

Question: {question}

Instructions:
- Réponds de manière précise et professionnelle
- Base-toi UNIQUEMENT sur le contexte fourni
- Cite la source [chunk_{chunk_id}]
- Sois détaillé mais concis
- Utilise le vocabulaire métier approprié"""
            }
        ]

        try:
            response = llm_provider.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )

            answer = response['content']

            return {
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            }

        except Exception as e:
            print(f"[ERREUR] Génération pour chunk {chunk_id}: {e}")
            return None

    def generate(self, input_file: str, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Génère des exemples avec un LLM.

        Args:
            input_file: Fichier JSONL de chunks
            count: Nombre d'exemples à générer
            **kwargs:
                - llm_provider: Instance du provider LLM (requis)
                - seed: Seed pour reproductibilité

        Returns:
            Liste d'exemples au format training
        """
        llm_provider = kwargs.get('llm_provider')
        if not llm_provider:
            raise ValueError("llm_provider est requis pour LLMBasedGenerator")

        seed = kwargs.get('seed', 42)
        random.seed(seed)

        # Charger chunks
        chunks = self.load_chunks(input_file)

        # Sélectionner des chunks aléatoires
        selected_chunks = random.sample(chunks, min(count, len(chunks)))

        # Générer Q&A avec LLM
        dataset = []
        for i, chunk in enumerate(selected_chunks, 1):
            print(f"[{i}/{count}] Génération pour chunk {chunk.get('id', 'unknown')}...", end=' ')

            qa = self.generate_qa_from_chunk(chunk, llm_provider)

            if qa:
                dataset.append(qa)
                print("[OK]")
            else:
                print("[ECHEC]")

            # Pause pour rate limiting
            if i % 10 == 0:
                import time
                time.sleep(1)

        return dataset


class AugmentedGenerator(DatasetGenerator):
    """
    Générateur avec data augmentation.

    Génère de multiples variantes de questions pour chaque information
    et combine plusieurs informations pour créer un dataset large.

    Inspiré de: scripts/generate_training_large.py
    """

    SYSTEM_PROMPT = """Tu es un assistant spécialisé dans les applications du système d'information.
Tu réponds aux questions de manière précise, détaillée et professionnelle.
Tu te bases uniquement sur les informations factuelles disponibles.
Tu cites toujours tes sources en indiquant les IDs des chunks utilisés."""

    QUESTION_VARIANTS = {
        'hebergement': [
            "Qui héberge {app} ?",
            "Quel est l'hébergeur de {app} ?",
            "Où est hébergé {app} ?",
            "Où est hébergée l'application {app} ?",
            "Quel data center héberge {app} ?",
            "Quelle est l'infrastructure d'hébergement de {app} ?",
        ],
        'technologies': [
            "Quelles technologies utilise {app} ?",
            "Quelle est la technologie principale de {app} ?",
            "Sur quelles technologies repose {app} ?",
            "Quel est le stack technologique de {app} ?",
            "Avec quelles technologies {app} est-elle développée ?",
            "Quelle technologie a été utilisée pour développer {app} ?",
        ],
        'domaine': [
            "Quel est le domaine métier de {app} ?",
            "Dans quel domaine s'inscrit {app} ?",
            "À quel domaine métier appartient {app} ?",
            "Quel domaine couvre l'application {app} ?",
            "{app} relève de quel domaine ?",
        ],
        'description': [
            "À quoi sert {app} ?",
            "Quelle est la fonction de {app} ?",
            "Quel est le rôle de {app} ?",
            "Que fait {app} ?",
            "Peux-tu décrire {app} ?",
            "Quelle est la description de {app} ?",
        ],
        'moa': [
            "Qui est la MOA de {app} ?",
            "Quelle est la maîtrise d'ouvrage de {app} ?",
            "Qui porte {app} en tant que MOA ?",
            "Quelle direction est MOA de {app} ?",
        ],
    }

    def extract_info_from_content(self, content: str) -> Dict[str, Optional[str]]:
        """Extrait toutes les informations d'un contenu."""
        info = {}

        # Hébergement
        match = re.search(r'Data center:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            info['hebergement'] = match.group(1).strip()
        else:
            match = re.search(r'Hébergement[^:]*:\s*([^\n]+)', content, re.IGNORECASE)
            if match:
                info['hebergement'] = match.group(1).strip()

        # Technologies
        match = re.search(r'Technologie principale[^:]*:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            info['technologies'] = match.group(1).strip()

        # Domaine
        match = re.search(r'Domaine métier[^:]*:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            info['domaine'] = match.group(1).strip()

        # MOA
        match = re.search(r'(?:MOA|Maîtrise d\'ouvrage)[^:]*:\s*([^\n]+)', content, re.IGNORECASE)
        if match:
            info['moa'] = match.group(1).strip()

        # Description (simplifiée)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Nom long' in line or 'Description' in line:
                if i + 1 < len(lines):
                    info['description'] = lines[i+1].strip()
                    break

        return info

    def generate_qa_for_app(self, app_id: str, app_name: str, chunks: List[Dict]) -> List[Dict]:
        """Génère toutes les Q&A possibles pour une app avec augmentation."""
        qa_pairs = []

        # Combiner le contenu
        full_content = '\n'.join([c.get('content', '') for c in chunks])

        # Extraire infos
        info = self.extract_info_from_content(full_content)

        # Générer variantes pour chaque type d'info
        for info_type, value in info.items():
            if value and info_type in self.QUESTION_VARIANTS:
                variants = self.QUESTION_VARIANTS[info_type]
                for variant_template in variants:
                    question = variant_template.format(app=app_name)

                    # Générer la réponse
                    if info_type == 'hebergement':
                        answer = f"{app_name} est hébergé par {value}. [Source: chunk_{app_id}]"
                    elif info_type == 'technologies':
                        answer = f"{app_name} utilise les technologies suivantes : {value}. [Source: chunk_{app_id}]"
                    elif info_type == 'domaine':
                        answer = f"{app_name} appartient au domaine métier : {value}. [Source: chunk_{app_id}]"
                    elif info_type == 'moa':
                        answer = f"La maîtrise d'ouvrage (MOA) de {app_name} est assurée par {value}. [Source: chunk_{app_id}]"
                    elif info_type == 'description':
                        answer = f"{app_name} : {value} [Source: chunk_{app_id}]"
                    else:
                        answer = f"{value} [Source: chunk_{app_id}]"

                    qa_pairs.append({
                        'question': question,
                        'answer': answer,
                        'app_name': app_name,
                        'type': info_type
                    })

        # Questions combinées
        if info.get('domaine') and info.get('technologies'):
            qa_pairs.append({
                'question': f"Quel est le domaine et les technologies de {app_name} ?",
                'answer': f"{app_name} appartient au domaine {info['domaine']} et utilise {info['technologies']}. [Source: chunk_{app_id}]",
                'app_name': app_name,
                'type': 'combined'
            })

        if info.get('hebergement') and info.get('moa'):
            qa_pairs.append({
                'question': f"Où est hébergé {app_name} et qui est la MOA ?",
                'answer': f"{app_name} est hébergé par {info['hebergement']} et la MOA est {info['moa']}. [Source: chunk_{app_id}]",
                'app_name': app_name,
                'type': 'combined'
            })

        return qa_pairs

    def generate(self, input_file: str, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Génère des exemples avec augmentation.

        Args:
            input_file: Fichier JSONL de chunks
            count: Nombre cible d'exemples
            **kwargs: seed (pour reproductibilité)

        Returns:
            Liste d'exemples au format training
        """
        seed = kwargs.get('seed', 42)
        random.seed(seed)

        # Charger chunks
        chunks = self.load_chunks(input_file)

        # Grouper par application
        apps = defaultdict(list)
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            app_id = metadata.get('id', 'unknown')
            apps[app_id].append(chunk)

        # Générer Q&A avec augmentation
        all_qa_pairs = []
        for app_id, app_chunks in apps.items():
            app_name = app_chunks[0].get('metadata', {}).get('nom', f'App_{app_id}')
            qa_pairs = self.generate_qa_for_app(app_id, app_name, app_chunks)
            all_qa_pairs.extend(qa_pairs)

        # Si pas assez, dupliquer avec mélange
        if len(all_qa_pairs) < count:
            repetitions = (count // len(all_qa_pairs)) + 1
            all_qa_pairs = all_qa_pairs * repetitions
            random.shuffle(all_qa_pairs)

        # Prendre le nombre demandé
        all_qa_pairs = all_qa_pairs[:count]

        # Convertir au format training
        examples = []
        for qa in all_qa_pairs:
            example = {
                'messages': [
                    {'role': 'system', 'content': self.SYSTEM_PROMPT},
                    {'role': 'user', 'content': qa['question']},
                    {'role': 'assistant', 'content': qa['answer']}
                ]
            }
            examples.append(example)

        return examples
