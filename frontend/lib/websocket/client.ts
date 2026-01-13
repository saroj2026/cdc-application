/**
 * WebSocket client for real-time monitoring
 */
import { io, Socket } from 'socket.io-client';
import { store } from '@/lib/store/store';
import { addReplicationEvent, addMonitoringMetric, fetchReplicationEvents } from '@/lib/store/slices/monitoringSlice';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000';

class WebSocketClient {
  private socket: Socket | null = null;
  private subscribedPipelines: Set<number | string> = new Set();
  private isConnecting: boolean = false;
  private connectionFailed: boolean = false; // Track if connection has failed to prevent retries

  connect() {
    // Prevent multiple connection attempts
    if (this.socket?.connected) {
      return;
    }
    
    if (this.isConnecting) {
      return;
    }

    // If connection has previously failed, don't retry (backend may not have Socket.IO)
    if (this.connectionFailed) {
      return;
    }

    this.isConnecting = true;

    this.socket = io(WS_URL, {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: false, // Disable automatic reconnection - backend may not have Socket.IO
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 0, // Don't attempt reconnection
      timeout: 5000, // Shorter timeout to fail faster
      forceNew: false, // Reuse existing connection if available
      autoConnect: true, // Still try to connect, but don't retry on failure
    });

    this.socket.on('connect', () => {
      console.log('========================================');
      console.log('[Frontend] WEBSOCKET CONNECTED');
      console.log('========================================');
      console.log('[Frontend] Socket ID:', this.socket?.id);
      console.log('[Frontend] Previously subscribed pipelines:', Array.from(this.subscribedPipelines));
      this.isConnecting = false;
      this.connectionFailed = false; // Reset failure flag on successful connection
      // Re-subscribe to previously subscribed pipelines
      this.subscribedPipelines.forEach((pipelineId) => {
        if (this.socket?.connected) {
          console.log(`[Frontend] Re-subscribing to pipeline: ${pipelineId}`);
          this.socket.emit('subscribe_pipeline', { pipeline_id: pipelineId });
        }
      });
      console.log('========================================');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.isConnecting = false;
      if (reason === 'io server disconnect') {
        // Server disconnected, try to reconnect manually
        this.socket?.connect();
      }
    });

    this.socket.on('connect_error', (error) => {
      // Suppress WebSocket connection errors - backend may not have Socket.IO configured
      // This is not critical for the application to function
      this.isConnecting = false;
      this.connectionFailed = true; // Mark as failed to prevent future attempts
      // Disable reconnection to prevent spam
      if (this.socket) {
        this.socket.io.reconnecting = false;
        // Disconnect to clean up
        this.socket.disconnect();
      }
      // Silently fail - WebSocket is optional for real-time updates
      // Don't log to console to avoid cluttering logs
    });

    this.socket.on('error', (error) => {
      // Suppress WebSocket errors - backend may not have Socket.IO configured
      // This is not critical for the application to function
      // Disable reconnection to prevent spam
      if (this.socket) {
        this.socket.io.reconnecting = false;
      }
      // Don't log to console to avoid cluttering logs
    });

    this.socket.on('replication_event', (data: any) => {
      try {
        console.log('========================================');
        console.log('[Frontend] RECEIVED REPLICATION EVENT');
        console.log('========================================');
        console.log('[Frontend] Event ID:', data.id);
        console.log('[Frontend] Pipeline ID:', data.pipeline_id);
        console.log('[Frontend] Event Type:', data.event_type);
        console.log('[Frontend] Table:', data.table_name);
        console.log('[Frontend] Status:', data.status);
        console.log('[Frontend] Full event data:', data);
        console.log('========================================');
        
        store.dispatch(addReplicationEvent(data));
        console.log('[Frontend] ✓ Event added to Redux store');
        
        // Refresh events from API with correct parameters when new event is received
        // This ensures the events list is up-to-date with all parameters applied
        const state = store.getState();
        const monitoringState = state.monitoring;
        const selectedPipelineId = monitoringState.selectedPipelineId;
        
        // Prepare fetch parameters based on current state
        const fetchParams: {
          pipelineId?: number | string;
          limit?: number;
          todayOnly?: boolean;
          startDate?: string | Date;
          endDate?: string | Date;
        } = {
          limit: 500,
          todayOnly: false, // Fetch all events, not just today's
        };
        
        // Add pipeline_id if a specific pipeline is selected, or use the event's pipeline_id
        if (selectedPipelineId) {
          fetchParams.pipelineId = selectedPipelineId;
        } else if (data.pipeline_id) {
          // If no pipeline is selected but event has pipeline_id, refresh with that pipeline
          fetchParams.pipelineId = data.pipeline_id;
        }
        
        // Dispatch fetch to refresh events list with correct parameters
        store.dispatch(fetchReplicationEvents(fetchParams));
        
        // Show browser notification for new events
        if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
          new Notification('CDC Event Captured', {
            body: `${data.event_type?.toUpperCase() || 'EVENT'} on ${data.table_name || 'table'} - ${data.status || 'unknown'}`,
            icon: '/icon-dark-32x32.png',
          });
        }
      } catch (error) {
        console.error('Error handling replication event:', error);
      }
    });

    this.socket.on('monitoring_metric', (data: any) => {
      try {
        console.log('Received monitoring metric:', data);
        store.dispatch(addMonitoringMetric(data));
      } catch (error) {
        console.error('Error handling monitoring metric:', error);
      }
    });

    this.socket.on('pipeline_status', (data: any) => {
      try {
        console.log('Pipeline status update:', data);
        // Handle pipeline status updates
      } catch (error) {
        console.error('Error handling pipeline status:', error);
      }
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.subscribedPipelines.clear();
      this.isConnecting = false;
    }
  }

  subscribePipeline(pipelineId: number | string) {
    // Validate pipeline ID
    if (!pipelineId || pipelineId === 'NaN' || pipelineId === 'undefined' || 
        (typeof pipelineId === 'number' && (isNaN(pipelineId) || !isFinite(pipelineId)))) {
      console.error(`[Frontend] ✗ Invalid pipeline ID for subscription: ${pipelineId}`);
      return;
    }
    
    // Skip if already subscribed
    if (this.subscribedPipelines.has(pipelineId)) {
      console.log(`[Frontend] Already subscribed to pipeline: ${pipelineId}`);
      return;
    }

    console.log(`[Frontend] ========================================`);
    console.log(`[Frontend] SUBSCRIBING TO PIPELINE`);
    console.log(`[Frontend] ========================================`);
    console.log(`[Frontend] Pipeline ID: ${pipelineId} (type: ${typeof pipelineId})`);
    console.log(`[Frontend] WebSocket connected: ${this.socket?.connected || false}`);
    console.log(`[Frontend] Socket ID: ${this.socket?.id || 'N/A'}`);

    // Add to set first to prevent duplicate subscriptions
    this.subscribedPipelines.add(pipelineId);

    if (!this.socket?.connected) {
      console.log(`[Frontend] WebSocket not connected, connecting...`);
      this.connect();
      // Wait for connection before subscribing
      if (this.socket) {
        this.socket.once('connect', () => {
          if (this.socket?.connected) {
            console.log(`[Frontend] WebSocket connected, subscribing to pipeline: ${pipelineId}`);
            this.socket.emit('subscribe_pipeline', { pipeline_id: pipelineId });
            console.log(`[Frontend] ✓ Subscription request sent for pipeline: ${pipelineId}`);
          }
        });
      }
    } else if (this.socket.connected) {
      // Already connected, subscribe immediately
      console.log(`[Frontend] WebSocket already connected, subscribing immediately`);
      this.socket.emit('subscribe_pipeline', { pipeline_id: pipelineId });
      console.log(`[Frontend] ✓ Subscription request sent for pipeline: ${pipelineId}`);
    }
    console.log(`[Frontend] ========================================`);
  }

  unsubscribePipeline(pipelineId: number | string) {
    if (this.socket && this.subscribedPipelines.has(pipelineId)) {
      this.socket.emit('unsubscribe_pipeline', { pipeline_id: pipelineId });
      this.subscribedPipelines.delete(pipelineId);
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

export const wsClient = new WebSocketClient();

