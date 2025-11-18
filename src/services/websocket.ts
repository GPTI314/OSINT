import { io, Socket } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:3000';

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(): void {
    if (this.socket?.connected) {
      return;
    }

    const token = localStorage.getItem('auth_token');
    this.socket = io(WS_URL, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.socket?.close();
      }
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  on(event: string, callback: (data: any) => void): void {
    this.socket?.on(event, callback);
  }

  off(event: string, callback?: (data: any) => void): void {
    this.socket?.off(event, callback);
  }

  emit(event: string, data?: any): void {
    this.socket?.emit(event, data);
  }

  // Subscribe to investigation updates
  subscribeToInvestigation(investigationId: string): void {
    this.emit('subscribe:investigation', { investigationId });
  }

  unsubscribeFromInvestigation(investigationId: string): void {
    this.emit('unsubscribe:investigation', { investigationId });
  }

  // Subscribe to job updates
  subscribeToJob(jobId: string, jobType: 'scraping' | 'crawling'): void {
    this.emit('subscribe:job', { jobId, jobType });
  }

  unsubscribeFromJob(jobId: string, jobType: 'scraping' | 'crawling'): void {
    this.emit('unsubscribe:job', { jobId, jobType });
  }
}

export const websocket = new WebSocketService();
