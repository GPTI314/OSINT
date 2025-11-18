/**
 * State manager for crawl resume capability
 */

import * as fs from 'fs';
import * as path from 'path';
import { CrawlState, QueueItem } from '../types';

export class StateManager {
  private readonly stateDir: string;
  private readonly stateFile: string;

  constructor(stateDir: string = '.crawl-state', crawlId: string = 'default') {
    this.stateDir = stateDir;
    this.stateFile = path.join(stateDir, `${crawlId}.json`);
  }

  /**
   * Save crawl state to disk
   */
  async saveState(state: CrawlState): Promise<void> {
    try {
      // Ensure directory exists
      if (!fs.existsSync(this.stateDir)) {
        fs.mkdirSync(this.stateDir, { recursive: true });
      }

      // Write state to file
      const stateJson = JSON.stringify(state, null, 2);
      fs.writeFileSync(this.stateFile, stateJson, 'utf-8');
    } catch (error) {
      throw new Error(`Failed to save crawl state: ${error}`);
    }
  }

  /**
   * Load crawl state from disk
   */
  async loadState(): Promise<CrawlState | null> {
    try {
      if (!fs.existsSync(this.stateFile)) {
        return null;
      }

      const stateJson = fs.readFileSync(this.stateFile, 'utf-8');
      const state = JSON.parse(stateJson);

      // Convert date strings back to Date objects
      state.timestamp = new Date(state.timestamp);
      state.stats.startTime = new Date(state.stats.startTime);
      if (state.stats.endTime) {
        state.stats.endTime = new Date(state.stats.endTime);
      }

      state.errors = state.errors.map((error: any) => ({
        ...error,
        timestamp: new Date(error.timestamp),
        error: new Error(error.error.message),
      }));

      return state;
    } catch (error) {
      console.error(`Failed to load crawl state: ${error}`);
      return null;
    }
  }

  /**
   * Check if state exists
   */
  hasState(): boolean {
    return fs.existsSync(this.stateFile);
  }

  /**
   * Clear saved state
   */
  async clearState(): Promise<void> {
    try {
      if (fs.existsSync(this.stateFile)) {
        fs.unlinkSync(this.stateFile);
      }
    } catch (error) {
      throw new Error(`Failed to clear crawl state: ${error}`);
    }
  }

  /**
   * Get state file path
   */
  getStateFilePath(): string {
    return this.stateFile;
  }

  /**
   * Save checkpoint (partial state save during crawl)
   */
  async saveCheckpoint(
    visited: Set<string>,
    queue: QueueItem[],
    stats: any
  ): Promise<void> {
    try {
      const checkpoint = {
        visited: Array.from(visited),
        queue,
        stats,
        timestamp: new Date(),
      };

      const checkpointFile = this.stateFile.replace('.json', '.checkpoint.json');

      // Ensure directory exists
      if (!fs.existsSync(this.stateDir)) {
        fs.mkdirSync(this.stateDir, { recursive: true });
      }

      fs.writeFileSync(checkpointFile, JSON.stringify(checkpoint, null, 2), 'utf-8');
    } catch (error) {
      console.error(`Failed to save checkpoint: ${error}`);
    }
  }

  /**
   * Load checkpoint
   */
  async loadCheckpoint(): Promise<any | null> {
    try {
      const checkpointFile = this.stateFile.replace('.json', '.checkpoint.json');

      if (!fs.existsSync(checkpointFile)) {
        return null;
      }

      const checkpointJson = fs.readFileSync(checkpointFile, 'utf-8');
      return JSON.parse(checkpointJson);
    } catch (error) {
      console.error(`Failed to load checkpoint: ${error}`);
      return null;
    }
  }
}
