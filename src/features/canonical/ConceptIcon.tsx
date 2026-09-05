interface ConceptIconProps {
  readonly category: string;
}

export function ConceptIcon({
  category,
}: ConceptIconProps) {
  const key = category.toUpperCase();

  if (key.includes("LANGUAGE")) {
    return <span className="concept-icon">Aa</span>;
  }

  if (key.includes("REGISTRY")) {
    return <span className="concept-icon">DB</span>;
  }

  if (key.includes("MEASUREMENT")) {
    return <span className="concept-icon">▥</span>;
  }

  if (key.includes("LLM")) {
    return <span className="concept-icon">▣</span>;
  }

  if (key.includes("LIFECYCLE")) {
    return <span className="concept-icon">↻</span>;
  }

  if (key.includes("RUNTIME")) {
    return <span className="concept-icon">◇</span>;
  }

  return null;
}
