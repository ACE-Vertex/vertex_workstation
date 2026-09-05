import type {
  VertexAdapter,
  VertexAdapterId,
} from "./types";

export class VertexAdapterRegistry {
  private readonly adapters =
    new Map<VertexAdapterId, VertexAdapter>();

  register(adapter: VertexAdapter): void {
    if (
      this.adapters.has(
        adapter.descriptor.id,
      )
    ) {
      throw new Error(
        `ADAPTER_DUPLICATE_ID:${adapter.descriptor.id}`,
      );
    }

    this.adapters.set(
      adapter.descriptor.id,
      adapter,
    );
  }

  get(
    id: VertexAdapterId,
  ): VertexAdapter {
    const adapter =
      this.adapters.get(id);

    if (!adapter) {
      throw new Error(
        `ADAPTER_NOT_REGISTERED:${id}`,
      );
    }

    return adapter;
  }

  list(): readonly VertexAdapter[] {
    return [
      ...this.adapters.values(),
    ];
  }
}
