# Adaptive Dialogue Generator for NPCs in Video Games

This project aims to assist game developers in creating dynamic and context-sensitive dialogues for Non-Player Characters (NPCs) in video games, using Natural Language Processing (NLP) techniques. The tool generates personalized dialogue options based on player actions and context, while giving developers control over the final content.

## Technologies Used

- **spaCy**: Used for linguistic manipulation, including text structuring and context embedding.
- **T5 (Text-to-Text Transfer Transformer)**: Used for generating context-aware dialogue options based on the player’s past actions and character traits.
- **BERT**: Utilized for selecting the most contextually relevant dialogue from the generated options.
- **Streamlit / Gradio**: For creating an interactive interface to test and refine the generated dialogues in real-time.

## Project Objective

The tool generates multiple dialogue options for NPCs based on the player's achievements and context (e.g., quests completed, character status). The developer selects the most appropriate options to ensure coherence with the game’s narrative. This hybrid AI-assisted approach improves the depth and personalization of NPC-player interactions.

## Demo

An interactive demo is provided via Streamlit or Gradio to test the generated dialogues in real-time.
