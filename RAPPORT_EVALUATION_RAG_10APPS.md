# Rapport d'Évaluation RAG - 10 Applications

**Date**: 2025-12-21
**Dataset**: questions_10apps_finetuning.jsonl (205 questions)
**Questions testées**: 20 premières questions
**Collection**: applications_10apps (88 chunks)
**Modèle LLM**: ollama/llama3.2:latest
**Chunks par question**: 5

---

## 📊 Résumé Exécutif

### Métriques Techniques
| Métrique | Valeur |
|----------|--------|
| **Taux de succès technique** | 100% (20/20) |
| **Temps moyen par question** | 195.5s (~3min 15s) |
| **Tokens moyens par réponse** | 931 tokens |
| **Temps total** | 65.2 minutes |
| **Tokens total** | 18,614 tokens |

### Métriques Qualitatives ⚠️
| Métrique | Valeur | Commentaire |
|----------|--------|-------------|
| **Réponses correctes** | **0/20 (0%)** | Aucune réponse ne correspond à l'attendu |
| **Réponses partielles** | 3/20 (15%) | Information fragmentaire trouvée |
| **Réponses incorrectes** | 17/20 (85%) | Information totalement absente ou erronée |

---

## 🔍 Analyse Détaillée par Question

### Questions sur le **Statut** (Q1-Q3)

#### Q1: "L'application 6Tzen est-elle en production ?"
- **Attendu**: `L'application 6Tzen a le statut En production.`
- **Obtenu**: Long paragraphe de 1115 tokens disant "je n'ai pas trouvé d'information clairement indiquant que l'application 6Tzen est en production"
- **Chunks**: chunk_29, chunk_42, chunk_41, chunk_20, chunk_3
- **Temps**: 290.0s
- **Analyse**: ❌ Le système ne trouve PAS le statut de 6Tzen malgré 5 chunks retournés

#### Q2: "Dans quel état se trouve l'application 6Tzen ?"
- **Attendu**: `L'application 6Tzen a le statut En production.`
- **Obtenu**: "je n'ai pas trouvé d'informations sur une application appelée '6Tzen'"
- **Chunks**: chunk_20, chunk_29, chunk_26, chunk_42, chunk_50
- **Temps**: 122.1s
- **Analyse**: ❌ Le système ne reconnaît même pas l'existence de 6Tzen

#### Q3: "Quel est le statut de 6Tzen ?"
- **Attendu**: `L'application 6Tzen a le statut En production.`
- **Obtenu**: "Je ne possède pas d'information sur ce sujet [ID: chunk_49]"
- **Chunks**: chunk_49, chunk_20, chunk_42, chunk_69, chunk_84
- **Temps**: 91.3s
- **Analyse**: ❌ Échec complet - aucune information trouvée

**Constat**: Sur 3 formulations différentes de la même question, **0% de succès**

---

### Questions sur le **Nom Complet** (Q4-Q5)

#### Q4: "Quelle est la dénomination complète de l'application 6Tzen ?"
- **Attendu**: `Outil national de dématérialisation des démarches des transports routiers`
- **Obtenu**: "je n'ai trouvé aucune information sur une application appelée '6Tzen'"
- **Chunks**: chunk_20, chunk_29, chunk_60, chunk_26, chunk_50
- **Temps**: 130.3s
- **Analyse**: ❌ Échec total

#### Q5: "Quel est le nom complet de 6Tzen ?"
- **Attendu**: `Outil national de dématérialisation des démarches des transports routiers`
- **Obtenu**: "6Tzen Admin" (extrait d'un email)
- **Chunks**: chunk_5, chunk_29, chunk_49, chunk_84, chunk_42
- **Temps**: 132.4s
- **Analyse**: ⚠️ Réponse INCORRECTE - confond le nom d'un contact avec le nom de l'application

---

### Questions sur l'**Identifiant** (Q6-Q7)

#### Q6: "Quel est l'identifiant de 6Tzen ?"
- **Attendu**: `1238`
- **Obtenu**: `6tzen-admin.ged.ds.msp.dnum.sg@developpement-durable.gouv.fr` (email)
- **Chunks**: chunk_50, chunk_49, chunk_20, chunk_42, chunk_5
- **Temps**: 96.1s
- **Analyse**: ❌ Confond l'ID de l'application avec un email de contact

#### Q7: "Quel est l'ID de l'application 6Tzen ?"
- **Attendu**: `1238`
- **Obtenu**: "chunk_60" (confond l'ID du chunk avec l'ID de l'application!)
- **Chunks**: chunk_20, chunk_29, chunk_5, chunk_26, chunk_60
- **Temps**: 121.0s
- **Analyse**: ❌ Erreur grave - confond chunk ID avec app ID

---

### Questions sur la **Portée Géographique** (Q8-Q9)

#### Q8: "Quelle est la portée géographique de 6Tzen ?"
- **Attendu**: `Nationale`
- **Obtenu**: "je n'ai pas trouvé d'information sur '6Tzen'"
- **Chunks**: chunk_37, chunk_31, chunk_7, chunk_87, chunk_59
- **Temps**: 271.3s (plus longue réponse!)
- **Analyse**: ❌ Aucune information trouvée

#### Q9: "L'application 6Tzen est-elle nationale ou locale ?"
- **Attendu**: `Nationale`
- **Obtenu**: "je n'ai pas trouvé d'informations suffisantes pour déterminer si l'application 6Tzen est nationale ou locale"
- **Chunks**: chunk_20, chunk_73, chunk_61, chunk_26, chunk_42
- **Temps**: 162.3s
- **Analyse**: ❌ Information non trouvée

---

### Questions sur les **Domaines Métier** (Q10-Q12)

#### Q10: "À quels domaines métier appartient 6Tzen ?"
- **Attendu**: `L'application 6Tzen intervient dans le domaine Transports routiers.`
- **Obtenu**: "je ne trouve aucune information sur un '6Tzen'"
- **Chunks**: chunk_64, chunk_29, chunk_84, chunk_77, chunk_72
- **Temps**: 268.0s
- **Analyse**: ❌ Aucune information sur les domaines

#### Q11: "Dans quels domaines intervient l'application 6Tzen ?"
- **Attendu**: `L'application 6Tzen intervient dans le domaine Transports routiers.`
- **Obtenu**: "domaine des démarches simplifiées pour les autorisations d'urbanisme"
- **Chunks**: chunk_29, chunk_72, chunk_20, chunk_64, chunk_60
- **Temps**: 186.4s
- **Analyse**: ❌ Domaine TOTALEMENT INCORRECT (urbanisme au lieu de transports)

#### Q12: "Quels sont les domaines métier de 6Tzen ?"
- **Attendu**: `L'application 6Tzen intervient dans le domaine Transports routiers.`
- **Obtenu**: Longue réponse générique sur l'accès libre, la santé, l'éducation... mais PAS de transports routiers
- **Chunks**: chunk_50, chunk_20, chunk_84, chunk_37, chunk_29
- **Temps**: 261.7s
- **Analyse**: ❌ Hallucination - invente des domaines non pertinents

---

### Questions sur l'**Objectif/Description** (Q13-Q15)

#### Q13: "Quel est l'objectif de 6Tzen ?"
- **Attendu**: `La dématérialisation des procédures administratives du registre des entreprises de transport par route...` (texte long)
- **Obtenu**: "je n'ai pas d'informations sur '6Tzen'"
- **Chunks**: chunk_50, chunk_29, chunk_49, chunk_84, chunk_42
- **Temps**: 139.3s
- **Analyse**: ❌ Aucune description trouvée

#### Q14: "Quelle est la description de 6Tzen ?"
- **Attendu**: `La dématérialisation des procédures administratives...`
- **Obtenu**: "6Tzen est une application liée au développement durable" (très vague)
- **Chunks**: chunk_50, chunk_42, chunk_84, chunk_5, chunk_29
- **Temps**: 121.6s
- **Analyse**: ❌ Information extrêmement vague et incomplète

#### Q15: "À quoi sert l'application 6Tzen ?"
- **Attendu**: `La dématérialisation des procédures administratives...`
- **Obtenu**: Longue réponse (1649 tokens) mentionnant "dématérialisation des procédures administratives du registre des entreprises de transport par route"
- **Chunks**: chunk_29, chunk_5, chunk_72, chunk_42, chunk_0
- **Temps**: 498.3s (la plus longue!)
- **Analyse**: ✅ **RÉPONSE PARTIELLEMENT CORRECTE** - Première vraie réponse pertinente!

---

### Questions sur les **Contacts** (Q16-Q18)

#### Q16: "Quels sont les contacts de l'application 6Tzen ?"
- **Attendu**: `6Tzen Admin - SG/DNUM/MSP/DS/GED <6tzen-admin.ged.ds.msp.dnum.sg@developpement-durable.gouv.fr>`
- **Obtenu**: "je ne trouve aucune information directe sur les contacts de l'application 6Tzen"
- **Chunks**: chunk_20, chunk_26, chunk_29, chunk_60, chunk_5
- **Temps**: 198.8s
- **Analyse**: ❌ L'email existe dans chunk_5 mais n'est pas reconnu comme contact de 6Tzen

#### Q17: "Comment contacter l'équipe de 6Tzen ?"
- **Attendu**: `6Tzen Admin - SG/DNUM/MSP/DS/GED <6tzen-admin...>`
- **Obtenu**: "contactez l'intrapreneur" (réponse générique)
- **Chunks**: chunk_5, chunk_20, chunk_49, chunk_50, chunk_26
- **Temps**: 234.6s
- **Analyse**: ❌ Réponse évasive - l'email de contact est dans chunk_5 mais non détecté

#### Q18: "Qui est le contact principal pour 6Tzen ?"
- **Attendu**: `6Tzen Admin - SG/DNUM/MSP/DS/GED <6tzen-admin...>`
- **Obtenu**: `6tzen-admin.ged.ds.msp.dnum.sg@developpement-durable.gouv.fr` (email seul, sans contexte complet)
- **Chunks**: chunk_20, chunk_49, chunk_26, chunk_5, chunk_50
- **Temps**: 126.2s
- **Analyse**: ⚠️ **RÉPONSE PARTIELLE** - Email correct mais nom incomplet

---

### Questions sur la **Date de Production** (Q19-Q20)

#### Q19: "Quand 6Tzen a-t-elle été mise en production ?"
- **Attendu**: `10/02/2020`
- **Obtenu**: Mentionne "10/02/2020" mais dit "je ne trouve aucune information sur un système ou une application appelée '6Tzen'"
- **Chunks**: chunk_3, chunk_42, chunk_41, chunk_84, chunk_50
- **Temps**: 290.0s
- **Analyse**: ⚠️ **RÉPONSE CONTRADICTOIRE** - La date est là mais non associée à 6Tzen

#### Q20: "Quelle est la date de mise en production de 6Tzen ?"
- **Attendu**: `10/02/2020`
- **Obtenu**: "je n'ai trouvé aucune information sur la date de mise en production de 6Tzen" puis mentionne ADAU mis en production le 10/02/2020
- **Chunks**: chunk_3, chunk_41, chunk_59, chunk_20, chunk_14
- **Temps**: 167.6s
- **Analyse**: ❌ Trouve la date mais l'attribue à une AUTRE application (ADAU)

---

## 🔬 Analyse des Chunks Retournés

### Chunks les Plus Fréquents

| Chunk ID | Fréquence | Observations |
|----------|-----------|--------------|
| chunk_20 | 13/20 questions | Chunk sur "Access Libre" (AUTRE application!) |
| chunk_29 | 11/20 questions | Chunk sur "Démarches Simplifiées" |
| chunk_5 | 8/20 questions | Chunk contenant l'email 6Tzen Admin |
| chunk_42 | 8/20 questions | Chunk non pertinent |
| chunk_50 | 7/20 questions | Chunk sur "catégories de finalités" |

### Problème Majeur Identifié

**Les chunks retournés parlent d'AUTRES applications**, notamment:
- **Access Libre** (chunk_20) - Application d'accessibilité PMR
- **ADAU** (chunk_3) - Autorisations d'urbanisme
- **ADES** (chunk_29) - Données eaux souterraines
- **Access Cité** (chunk_26) - Accès services publics

**Le chunk contenant les informations de 6Tzen n'est JAMAIS retourné en premier.**

---

## 📈 Distribution des Temps de Réponse

```
0-100s   : 3 questions  (15%)  ████
100-200s : 10 questions (50%)  ████████████████████
200-300s : 6 questions  (30%)  ████████████
300-500s : 1 question   (5%)   ██
```

**Constat**: Aucune corrélation entre temps de réponse et qualité. Les réponses les plus longues (498s) ne sont pas meilleures.

---

## 💡 Réponses Correctes ou Partielles (3/20)

### Q15: "À quoi sert l'application 6Tzen ?" ✅
- **Temps**: 498.3s
- **Tokens**: 1649
- **Analyse**: La SEULE réponse vraiment pertinente. Le système a trouvé "dématérialisation des procédures administratives du registre des entreprises de transport par route"
- **Chunk clé**: chunk_0 (nouveau chunk pas vu ailleurs!)

### Q18: "Qui est le contact principal pour 6Tzen ?" ⚠️
- **Temps**: 126.2s
- **Réponse partielle**: Email correct mais nom incomplet

### Q19: "Quand 6Tzen a-t-elle été mise en production ?" ⚠️
- **Temps**: 290.0s
- **Réponse contradictoire**: Date mentionnée (10/02/2020) mais non associée à 6Tzen

---

## 🚨 Problèmes Critiques Identifiés

### 1. **Chunking Inefficace** (Critique)
- Les chunks retournés ne contiennent PAS les informations de 6Tzen
- La stratégie markdown-headers crée des chunks trop granulaires
- Perte de contexte entre les sections

**Exemple**: L'information "6Tzen" est peut-être dans un header, mais le contenu est dans un autre chunk

### 2. **Similarité Sémantique Défaillante** (Critique)
- La question "Quel est le statut de 6Tzen ?" retourne des chunks sur Access Libre, ADAU, ADES
- Aucune reconnaissance de "6Tzen" comme entité distincte
- Les embeddings ne capturent pas l'importance du nom de l'application

### 3. **Confusion Entre Applications** (Majeur)
- Q11: Le système confond 6Tzen avec des applications d'urbanisme
- Q20: La date de 6Tzen est attribuée à ADAU
- Le modèle LLM mélange les informations de différentes applications

### 4. **Hallucinations** (Majeur)
- Q12: Invente des domaines (santé, éducation) non mentionnés
- Q7: Confond chunk ID avec application ID
- Q6: Confond email de contact avec identifiant d'application

### 5. **Réponses Trop Verbeuses** (Mineur)
- Moyenne: 931 tokens par réponse
- Beaucoup de "bonjour", "je suis désolé", formulations répétitives
- Réponse la plus longue: 1649 tokens pour dire essentiellement une phrase

---

## 🎯 Recommandations

### Immédiat (Priorité 1) 🔴

1. **Revoir la Stratégie de Chunking**
   ```bash
   # Au lieu de markdown-headers
   dyag prepare-rag apps.md --chunking-method size-based \
     --chunk-size 1500 \
     --chunk-overlap 300
   ```
   - Chunks plus larges pour conserver le contexte
   - Overlap pour éviter la perte d'informations aux frontières

2. **Améliorer les Métadonnées des Chunks**
   - Ajouter l'ID de l'application (1238) dans les métadonnées
   - Ajouter le nom de l'application dans chaque chunk
   - Faciliter le filtrage par application

### Court Terme (Priorité 2) 🟡

3. **Optimiser le Prompt Système**
   - Réduire la verbosité ("Sois concis")
   - Éviter les hallucinations ("Base-toi UNIQUEMENT sur le contexte fourni")
   - Format de réponse structuré

4. **Tester Différents Modèles d'Embedding**
   - Tester `all-mpnet-base-v2` (meilleur que MiniLM)
   - Comparer avec `multilingual-e5-large` (pour le français)

### Moyen Terme (Priorité 3) 🟢

5. **Implémenter le Hybrid Search**
   - Combiner similarité sémantique + recherche par mots-clés
   - Boosting sur le nom de l'application

6. **Ajouter un Système de Reranking**
   - Re-classer les chunks retournés
   - Privilégier les chunks mentionnant explicitement "6Tzen"

7. **Créer des Tests de Régression**
   - Dataset de 20-30 questions critiques
   - Exécution automatique après chaque modification
   - Seuil minimal: 80% de réponses correctes

---

## 📊 Comparaison Attendu vs Obtenu - Tableau Synthétique

| # | Question | Attendu | Obtenu | Match | Temps |
|---|----------|---------|--------|-------|-------|
| 1 | Statut production? | En production | "pas d'info" | ❌ 0% | 290s |
| 2 | État application? | En production | "pas trouvé" | ❌ 0% | 122s |
| 3 | Statut 6Tzen? | En production | "pas d'info" | ❌ 0% | 91s |
| 4 | Dénomination complète? | Outil nat. démat. transport | "pas trouvé" | ❌ 0% | 130s |
| 5 | Nom complet? | Outil nat. démat. transport | "6Tzen Admin" (email) | ❌ 10% | 132s |
| 6 | Identifiant? | 1238 | email | ❌ 0% | 96s |
| 7 | ID application? | 1238 | chunk_60 | ❌ 0% | 121s |
| 8 | Portée géo? | Nationale | "pas trouvé" | ❌ 0% | 271s |
| 9 | Nationale/locale? | Nationale | "insuffisant" | ❌ 0% | 162s |
| 10 | Domaines métier? | Transports routiers | "pas trouvé" | ❌ 0% | 268s |
| 11 | Domaines intervention? | Transports routiers | Urbanisme | ❌ 0% | 186s |
| 12 | Domaines métier? | Transports routiers | Santé/éducation | ❌ 0% | 262s |
| 13 | Objectif? | Dématérialisation... | "pas d'info" | ❌ 0% | 139s |
| 14 | Description? | Dématérialisation... | "développement durable" | ❌ 5% | 122s |
| 15 | À quoi sert? | Dématérialisation... | Dématérialisation transport | ✅ 80% | 498s |
| 16 | Contacts? | Email+nom | "pas trouvé" | ❌ 0% | 199s |
| 17 | Contacter équipe? | Email+nom | "intrapreneur" | ❌ 10% | 235s |
| 18 | Contact principal? | Email+nom | Email seul | ⚠️ 50% | 126s |
| 19 | Quand production? | 10/02/2020 | "pas trouvé" (mais date mentionnée) | ⚠️ 30% | 290s |
| 20 | Date production? | 10/02/2020 | Date attribuée à ADAU | ❌ 0% | 168s |

**Score moyen de correspondance**: **8.5%**

---

## 🏁 Conclusion

### Points Positifs ✅
- **Stabilité technique**: 100% des requêtes ont abouti sans erreur
- **Performance**: Temps de réponse acceptable (~3min par question)
- **Une réponse correcte**: Q15 montre que le système PEUT fonctionner

### Points Négatifs ❌
- **Taux de réussite catastrophique**: 8.5% de correspondance moyenne
- **Chunking inadapté**: Les bons chunks ne sont jamais retournés
- **Confusion entre applications**: Le système mélange 6Tzen avec d'autres apps
- **Hallucinations**: Invente des informations non présentes dans les chunks

### Verdict Final
⚠️ **Le système RAG actuel n'est PAS fonctionnel** pour répondre aux questions sur les applications.

**Causes principales**:
1. Stratégie de chunking (markdown-headers) inadaptée
2. Embeddings qui ne capturent pas l'identité des applications
3. Absence de métadonnées discriminantes

**Action immédiate requise**: Refaire le chunking avec size-based (1500 tokens, overlap 300)

---

**Rapport généré automatiquement par Claude Code**
**Date**: 2025-12-21
**Version DYAG**: 0.8.0+
