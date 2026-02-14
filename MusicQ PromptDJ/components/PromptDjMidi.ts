
/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/
import { css, html, LitElement } from 'lit';
import { customElement, property, state, query } from 'lit/decorators.js';
import { styleMap } from 'lit/directives/style-map.js';

import { throttle } from '../utils/throttle';

import './PromptController';
import './PlayPauseButton';
import type { PlaybackState, Prompt } from '../types';
import { MidiDispatcher } from '../utils/MidiDispatcher';

/** The grid of prompt inputs for focus music. */
@customElement('prompt-dj-midi')
export class PromptDjMidi extends LitElement {
  // Removed override to fix compiler error regarding base class resolution
  static styles = css`
    :host {
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      box-sizing: border-box;
      position: relative;
      background-color: #0a0a0c;
      color: #e0e0e0;
    }
    #background {
      will-change: background-image;
      position: absolute;
      height: 100%;
      width: 100%;
      z-index: -1;
      background: #050507;
      opacity: 0.4;
    }
    #intent-container {
      width: 80vmin;
      display: flex;
      gap: 10px;
      margin-top: 5vh;
      margin-bottom: 2vh;
      z-index: 10;
    }
    #intent-input {
      flex: 1;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 8px;
      padding: 12px 20px;
      color: white;
      font-family: inherit;
      font-size: 1.1rem;
      outline: none;
      transition: all 0.3s ease;
    }
    #intent-input:focus {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(66, 133, 244, 0.6);
      box-shadow: 0 0 15px rgba(66, 133, 244, 0.2);
    }
    #sync-btn {
      background: #4285f4;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 0 24px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      white-space: nowrap;
    }
    #sync-btn:hover {
      background: #357ae8;
      box-shadow: 0 0 20px rgba(66, 133, 244, 0.4);
    }
    #sync-btn:disabled {
      background: #3c4043;
      cursor: not-allowed;
      opacity: 0.7;
    }
    #grid {
      width: 80vmin;
      height: 60vmin;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 2.5vmin;
      margin-bottom: 5vh;
    }
    prompt-controller {
      width: 100%;
    }
    play-pause-button {
      position: relative;
      width: 12vmin;
    }
    #top-bar {
      position: absolute;
      top: 0;
      width: 100%;
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-sizing: border-box;
    }
    .midi-controls {
      display: flex;
      gap: 10px;
    }
    button.tool-btn {
      font: inherit;
      font-weight: 600;
      cursor: pointer;
      color: #ccc;
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 6px;
      padding: 6px 12px;
      transition: all 0.2s;
    }
    button.tool-btn.active {
      background: #fff;
      color: #000;
      border-color: #fff;
    }
    select {
      font: inherit;
      padding: 6px;
      background: #1e1e21;
      color: #ccc;
      border-radius: 6px;
      border: 1px solid #3c4043;
      outline: none;
      cursor: pointer;
    }
    .syncing-spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 1s ease-in-out infinite;
      margin-right: 8px;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    @media (max-width: 600px) {
      #grid {
        grid-template-columns: repeat(2, 1fr);
        height: auto;
      }
      #intent-container {
        flex-direction: column;
        width: 90vmin;
      }
      #sync-btn {
        padding: 12px;
      }
    }
  `;

  @property({ type: Boolean }) private showMidi = false;
  @property({ type: String }) public playbackState: PlaybackState = 'stopped';
  @property({ type: Boolean }) public isSyncing = false;
  @state() public audioLevel = 0;
  @state() private midiInputIds: string[] = [];
  @state() private activeMidiInputId: string | null = null;
  @query('#intent-input') private intentInput!: HTMLInputElement;

  @property({ type: Object })
  private filteredPrompts = new Set<string>();

  private prompts: Map<string, Prompt>;
  private midiDispatcher: MidiDispatcher;

  constructor(initialPrompts: Map<string, Prompt>) {
    super();
    this.prompts = initialPrompts;
    this.midiDispatcher = new MidiDispatcher();
  }

  public getPrompts() {
    return this.prompts;
  }

  public updateAllPrompts(newPrompts: Map<string, Prompt>) {
    this.prompts = new Map(newPrompts);
    // Cast this to any to fix missing requestUpdate error in environment
    (this as any).requestUpdate();
  }

  private handlePromptChanged(e: CustomEvent<Prompt>) {
    const { promptId, text, weight, cc } = e.detail;
    const prompt = this.prompts.get(promptId);

    if (!prompt) return;

    prompt.text = text;
    prompt.weight = weight;
    prompt.cc = cc;

    const newPrompts = new Map(this.prompts);
    newPrompts.set(promptId, prompt);

    this.prompts = newPrompts;
    // Cast this to any to fix missing requestUpdate error in environment
    (this as any).requestUpdate();

    // Cast this to any to fix missing dispatchEvent error
    (this as any).dispatchEvent(
      new CustomEvent('prompts-changed', { detail: this.prompts }),
    );
  }

  private readonly makeBackground = throttle(() => {
    const clamp01 = (v: number) => Math.min(Math.max(v, 0), 1);
    const MAX_WEIGHT = 0.8;
    const MAX_ALPHA = 0.5;

    const bg: string[] = [];
    [...this.prompts.values()].forEach((p, i) => {
      const alphaPct = clamp01(p.weight / MAX_WEIGHT) * MAX_ALPHA;
      const alpha = Math.round(alphaPct * 0xff).toString(16).padStart(2, '0');
      const stop = p.weight / 2.5;
      const x = (i % 4) / 3;
      const y = Math.floor(i / 4) / 3;
      const s = `radial-gradient(circle at ${x * 100}% ${y * 100}%, ${p.color}${alpha} 0px, ${p.color}00 ${stop * 100}%)`;
      bg.push(s);
    });

    return bg.join(', ');
  }, 30);

  private toggleShowMidi() {
    return this.setShowMidi(!this.showMidi);
  }

  public async setShowMidi(show: boolean) {
    this.showMidi = show;
    if (!this.showMidi) return;
    try {
      const inputIds = await this.midiDispatcher.getMidiAccess();
      this.midiInputIds = inputIds;
      this.activeMidiInputId = this.midiDispatcher.activeMidiInputId;
    } catch (e: any) {
      this.showMidi = false;
      // Cast this to any to fix missing dispatchEvent error
      (this as any).dispatchEvent(new CustomEvent('error', { detail: e.message }));
    }
  }

  private handleMidiInputChange(event: Event) {
    const selectElement = event.target as HTMLSelectElement;
    this.activeMidiInputId = selectElement.value;
    this.midiDispatcher.activeMidiInputId = selectElement.value;
  }

  private handleSyncIntent() {
    const intent = this.intentInput.value;
    // Cast this to any to fix missing dispatchEvent error
    (this as any).dispatchEvent(new CustomEvent('sync-intent', { detail: intent }));
  }

  private playPause() {
    // Cast this to any to fix missing dispatchEvent error
    (this as any).dispatchEvent(new CustomEvent('play-pause'));
  }

  public addFilteredPrompt(prompt: string) {
    this.filteredPrompts = new Set([...this.filteredPrompts, prompt]);
  }

  // Removed override to fix compiler error regarding base class resolution
  render() {
    const bg = styleMap({ backgroundImage: this.makeBackground() });
    return html`
      <div id="background" style=${bg}></div>
      
      <div id="top-bar">
        <div style="font-weight: 700; font-size: 1.2rem; letter-spacing: 0.1em; opacity: 0.8;">FOCUS INTENT</div>
        <div class="midi-controls">
          <button
            @click=${this.toggleShowMidi}
            class="tool-btn ${this.showMidi ? 'active' : ''}">MIDI</button>
          <select
            @change=${this.handleMidiInputChange}
            .value=${this.activeMidiInputId || ''}
            style=${this.showMidi ? '' : 'visibility: hidden'}>
            ${this.midiInputIds.length > 0
              ? this.midiInputIds.map(id => html`<option value=${id}>${this.midiDispatcher.getDeviceName(id)}</option>`)
              : html`<option value="">No devices</option>`}
          </select>
        </div>
      </div>

      <div id="intent-container">
        <input 
          id="intent-input" 
          type="text" 
          placeholder="I want to focus on..." 
          @keydown=${(e: KeyboardEvent) => e.key === 'Enter' && this.handleSyncIntent()} />
        <button 
          id="sync-btn" 
          ?disabled=${this.isSyncing} 
          @click=${this.handleSyncIntent}>
          ${this.isSyncing ? html`<span class="syncing-spinner"></span>Syncing...` : 'Sync Focus'}
        </button>
      </div>

      <div id="grid">${this.renderPrompts()}</div>
      
      <play-pause-button 
        .playbackState=${this.playbackState} 
        @click=${this.playPause}></play-pause-button>
    `;
  }

  private renderPrompts() {
    return [...this.prompts.values()].map((prompt) => {
      return html`<prompt-controller
        promptId=${prompt.promptId}
        ?filtered=${this.filteredPrompts.has(prompt.text)}
        cc=${prompt.cc}
        text=${prompt.text}
        weight=${prompt.weight}
        color=${prompt.color}
        .midiDispatcher=${this.midiDispatcher}
        .showCC=${this.showMidi}
        audioLevel=${this.audioLevel}
        @prompt-changed=${this.handlePromptChanged}>
      </prompt-controller>`;
    });
  }
}
