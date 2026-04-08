# Synapse Test Corpus Source

This document is the source of truth for the real golden PDF set used by Synapse.

## Canonical Source

The real source PDFs currently live outside the repo at:

- `/Users/timsmykov/Desktop/Статьи для теста`

This path is the operator-owned source folder on the Mac workstation.

## Rule

- Do not treat `test_corpus/` inside the repo as the canonical source of the real PDFs.
- `test_corpus/` in the repo is for manifests, mirrors, fixture metadata, and test-side artifacts only.
- The actual research PDFs should be selected from `/Users/timsmykov/Desktop/Статьи для теста` and then synced to the server-side corpus location for execution.

## Server-First Policy

- Mac stores the source PDFs.
- Server runs ingest, tests, and runtime flows.
- CI must not depend on the Mac-local absolute path.

## Current Inventory

The current source folder contains the first candidate papers for golden fixture selection, including:

- `Acikgoz et al. (2023) - Consumer Engagement with AI Voice Assistants.pdf`
- `Belanche et al. (2021) - Robots Physical Appearance in Frontline Services.pdf`
- `Blut, M., et al. (2021) - Journal of the Academy of Marketing Science.pdf`
- `Bouhlal & Belahcen (2025) - Conversational AI and Consumer Behavior.pdf`
- `Epley et al. (2007) — On seeing human- A three-factor theory of anthropomorphism.pdf`
- `Greilich et al. (2025) - Consumer Response to Anthropomorphism of AI Chatbots.pdf`
- `Handoyo (2024) - Trust, Risk, Security in E-commerce Meta-analysis.pdf`
- `Hardcastle et al. (2025) - Customer Responses to AI-Driven Personalization.pdf`
- `Hollebeek et al. (2021) - Customer Engagement in Automated Service.pdf`
- `Hollebeek et al. (2024) - Engaging Consumers Through AI Technologies.pdf`
- `Lopez-Lopez & Iniesta (2025) - Conversational AI Impact on Decision-Making.pdf`
- `Masciari et al. (2024) - AI Recommendation Systems and Ethics.pdf`
- `Mittameedi et al. (2025) - Customer Experience in E-Commerce and AI.pdf`
- `Nguyen et al. (2023) - Chatbots Anthropomorphism Customer Experience.pdf`
- `Oprea & Bra (2025) - AI Game-Changer in E-Business.pdf`
- `Prentice & Nguyen (2020) - Engaging Customers with AI and Employee Service.pdf`
- `Raji et al. (2024) - E-commerce AI Personalization Market Trends.pdf`
- `Reeves, B., & Nass, C. (1996) - The Media Equation (книга).pdf`
- `Yu et al. (2025) - Consumer Reactions to AI-Generated Content.pdf`

## Next Step

The next ingest-quality slice should choose 3-5 files from this folder, describe them in the manifest, sync them to the server corpus location, and run the first server-side ingest pass.
