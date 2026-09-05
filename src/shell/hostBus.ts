import type { VertexHostBus, VertexHostEvent } from "../contracts/unit";

export function createHostBus(): VertexHostBus {
  const subscribers = new Map<string, Set<(event: VertexHostEvent) => void>>();

  return {
    publish(event) {
      const handlers = subscribers.get(event.topic);
      if (!handlers) return;

      for (const handler of handlers) {
        handler(event);
      }
    },

    subscribe(topic, handler) {
      const handlers = subscribers.get(topic) ?? new Set();
      handlers.add(handler);
      subscribers.set(topic, handlers);

      return () => {
        const current = subscribers.get(topic);
        current?.delete(handler);
        if (current && current.size === 0) {
          subscribers.delete(topic);
        }
      };
    },
  };
}
