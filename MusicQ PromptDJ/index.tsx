
/**
 * @fileoverview Adapt real-time music for deep focus based on user intent.
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import type { PlaybackState, Prompt } from './types';
import { GoogleGenAI, Type } from '@google/genai';
import { PromptDjMidi } from './components/PromptDjMidi';
import { ToastMessage } from './components/ToastMessage';
import { LiveMusicHelper } from './utils/LiveMusicHelper';
import { AudioAnalyser } from './utils/AudioAnalyser';

// Use the standard API_KEY env variable
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
const musicModel = 'lyria-realtime-exp';
const intentModel = 'gemini-3-flash-preview';

async function main() {
  const initialPrompts = buildInitialPrompts();

  // @ts-ignore - Fix Node assignability and missing property errors by casting to any
  const pdjMidi = new PromptDjMidi(initialPrompts) as any;
  document.body.appendChild(pdjMidi);

  // @ts-ignore - Fix Node assignability error by casting to any
  const toastMessage = new ToastMessage() as any;
  document.body.appendChild(toastMessage);

  const liveMusicHelper = new LiveMusicHelper(ai, musicModel);
  liveMusicHelper.setWeightedPrompts(initialPrompts);

  const audioAnalyser = new AudioAnalyser(liveMusicHelper.audioContext);
  liveMusicHelper.extraDestination = audioAnalyser.node;

  pdjMidi.addEventListener('prompts-changed', ((e: Event) => {
    const customEvent = e as CustomEvent<Map<string, Prompt>>;
    const prompts = customEvent.detail;
    liveMusicHelper.setWeightedPrompts(prompts);
  }));

  pdjMidi.addEventListener('play-pause', () => {
    liveMusicHelper.playPause();
  });

  // Handle Intent Synchronization via Gemini
  pdjMidi.addEventListener('sync-intent', (async (e: Event) => {
    const customEvent = e as CustomEvent<string>;
    const intentText = customEvent.detail;
    
    if (!intentText.trim()) return;

    try {
      pdjMidi.isSyncing = true;
      const promptNames = Array.from(initialPrompts.values()).map(p => p.text);
      
      const response = await ai.models.generateContent({
        model: intentModel,
        contents: `I want to focus on: "${intentText}". 
        Given these 16 focus audio channels: ${JSON.stringify(promptNames)}, 
        return a JSON object where each key is the channel name and each value is a weight between 0.0 and 2.0. 
        Higher weights for channels that best support this specific intent. 
        Keep most channels at 0 or low weights (below 0.5) to maintain clarity, and pick 3-4 primary channels (1.0-2.0) to lead the soundscape.`,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: promptNames.reduce((acc, name) => {
              acc[name] = { type: Type.NUMBER };
              return acc;
            }, {} as any),
          }
        }
      });

      const weightsMap = JSON.parse(response.text);
      const updatedPrompts = new Map(pdjMidi.getPrompts());
      
      updatedPrompts.forEach((prompt, id) => {
        if (weightsMap[prompt.text] !== undefined) {
          prompt.weight = weightsMap[prompt.text];
        }
      });

      pdjMidi.updateAllPrompts(updatedPrompts);
      liveMusicHelper.setWeightedPrompts(updatedPrompts);
      toastMessage.show("Deep Focus intent synced successfully.");
    } catch (err: any) {
      console.error(err);
      toastMessage.show("Failed to sync intent: " + err.message);
    } finally {
      pdjMidi.isSyncing = false;
    }
  }) as any);

  liveMusicHelper.addEventListener('playback-state-changed', ((e: Event) => {
    const customEvent = e as CustomEvent<PlaybackState>;
    const playbackState = customEvent.detail;
    pdjMidi.playbackState = playbackState;
    playbackState === 'playing' ? audioAnalyser.start() : audioAnalyser.stop();
  }));

  liveMusicHelper.addEventListener('filtered-prompt', ((e: Event) => {
    const customEvent = e as CustomEvent<any>;
    const filteredPrompt = customEvent.detail;
    toastMessage.show(filteredPrompt.filteredReason!)
    pdjMidi.addFilteredPrompt(filteredPrompt.text!);
  }));

  const errorToast = ((e: Event) => {
    const customEvent = e as CustomEvent<string>;
    const error = customEvent.detail;
    toastMessage.show(error);
  });

  liveMusicHelper.addEventListener('error', errorToast);
  pdjMidi.addEventListener('error', errorToast);

  audioAnalyser.addEventListener('audio-level-changed', ((e: Event) => {
    const customEvent = e as CustomEvent<number>;
    const level = customEvent.detail;
    pdjMidi.audioLevel = level;
  }));

}

function buildInitialPrompts() {
  const prompts = new Map<string, Prompt>();

  for (let i = 0; i < DEFAULT_PROMPTS.length; i++) {
    const promptId = `prompt-${i}`;
    const prompt = DEFAULT_PROMPTS[i];
    const { text, color } = prompt;
    prompts.set(promptId, {
      promptId,
      text,
      weight: i === 0 || i === 4 ? 1 : 0, // Start with some defaults
      cc: i,
      color,
    });
  }

  return prompts;
}

const DEFAULT_PROMPTS = [
  { color: '#2c3e50', text: 'Binaural Alpha (8-13Hz)' },
  { color: '#2980b9', text: 'Deep Brown Noise' },
  { color: '#8e44ad', text: 'Lo-fi Study Beats' },
  { color: '#16a085', text: 'Space Station Drone' },
  { color: '#34495e', text: 'Rainy Library' },
  { color: '#2ecc71', text: 'Minimalist Piano' },
  { color: '#9b59b6', text: 'Ethereal Pads' },
  { color: '#f39c12', text: 'Gentle Woodwinds' },
  { color: '#e67e22', text: 'Forest Birds' },
  { color: '#3498db', text: 'Underwater Hum' },
  { color: '#1abc9c', text: 'Clock Ticking' },
  { color: '#7f8c8d', text: 'White Noise' },
  { color: '#c0392b', text: 'Vinyl Crackle' },
  { color: '#d35400', text: 'Thrumming Engine' },
  { color: '#27ae60', text: 'Quiet Garden' },
  { color: '#4b0082', text: 'Gregorian Chant' },
];

main();
