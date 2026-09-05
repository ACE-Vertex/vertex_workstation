import type {
  RayFileContent,
  RayFinding,
  RayLexicalFacts,
  RayLineFact,
  RayMode,
} from "./models";

type RayLanguage =
  | "python"
  | "typescript"
  | "javascript"
  | "rust"
  | "css"
  | "generic";

function unique(values: string[], limit: number): string[] {
  return [...new Set(values)].slice(0, limit);
}

function uniqueNumbers(values: number[], limit: number): number[] {
  return [...new Set(values)].slice(0, limit);
}

function languageFor(source: RayFileContent): RayLanguage {
  const path = source.relativePath.toLowerCase();
  if (path.endsWith(".py")) return "python";
  if (path.endsWith(".ts") || path.endsWith(".tsx")) return "typescript";
  if (path.endsWith(".js") || path.endsWith(".jsx") || path.endsWith(".mjs") || path.endsWith(".cjs")) {
    return "javascript";
  }
  if (path.endsWith(".rs")) return "rust";
  if (path.endsWith(".css") || path.endsWith(".scss") || path.endsWith(".sass") || path.endsWith(".less")) {
    return "css";
  }
  return "generic";
}

function firstColumn(line: string, token: string): number {
  const index = line.indexOf(token);
  return index >= 0 ? index + 1 : Math.max(1, line.search(/\S/) + 1);
}

function pushImport(
  target: RayLineFact[],
  line: string,
  lineNumber: number,
  name: string,
  kind: string,
) {
  target.push({
    name,
    kind,
    line: lineNumber,
    column: Math.max(1, line.search(/\S/) + 1),
    evidence: line.trim().slice(0, 260),
  });
}

function pushSymbol(
  target: RayLineFact[],
  line: string,
  lineNumber: number,
  name: string,
  kind: string,
) {
  target.push({
    name,
    kind,
    line: lineNumber,
    column: firstColumn(line, name),
    evidence: line.trim().slice(0, 260),
  });
}

function pythonFacts(
  line: string,
  lineNumber: number,
  importFacts: RayLineFact[],
  symbolFacts: RayLineFact[],
) {
  const trimmed = line.trim();

  const fromImport = trimmed.match(
    /^from\s+([A-Za-z_][\w.]*)\s+import\s+(.+)$/,
  );
  if (fromImport) {
    pushImport(
      importFacts,
      line,
      lineNumber,
      `${fromImport[1]} -> ${fromImport[2].trim()}`,
      "python-from-import",
    );
  } else {
    const directImport = trimmed.match(/^import\s+(.+)$/);
    if (directImport) {
      pushImport(
        importFacts,
        line,
        lineNumber,
        directImport[1].trim(),
        "python-import",
      );
    }
  }

  const decorator = trimmed.match(/^@([A-Za-z_][\w.]*)/);
  if (decorator) {
    pushSymbol(
      symbolFacts,
      line,
      lineNumber,
      decorator[1],
      "python-decorator",
    );
  }

  const asyncDef = trimmed.match(/^async\s+def\s+([A-Za-z_]\w*)\s*\(/);
  if (asyncDef) {
    pushSymbol(
      symbolFacts,
      line,
      lineNumber,
      asyncDef[1],
      "python-async-function",
    );
    return;
  }

  const fn = trimmed.match(/^def\s+([A-Za-z_]\w*)\s*\(/);
  if (fn) {
    pushSymbol(
      symbolFacts,
      line,
      lineNumber,
      fn[1],
      "python-function",
    );
    return;
  }

  const cls = trimmed.match(/^class\s+([A-Za-z_]\w*)\b/);
  if (cls) {
    pushSymbol(
      symbolFacts,
      line,
      lineNumber,
      cls[1],
      "python-class",
    );
    return;
  }

  // Only zero-indentation assignments are classified as module ownership facts.
  // Nested/local assignments are intentionally excluded from this pass.
  if (/^\S/.test(line) && !trimmed.startsWith("#")) {
    const annotatedBinding = line.match(
      /^([A-Za-z_]\w*)\s*:\s*[^=]+?=\s*/,
    );
    if (annotatedBinding) {
      pushSymbol(
        symbolFacts,
        line,
        lineNumber,
        annotatedBinding[1],
        "python-module-binding",
      );
      return;
    }

    const binding = line.match(/^([A-Za-z_]\w*)\s*=\s*/);
    if (binding) {
      pushSymbol(
        symbolFacts,
        line,
        lineNumber,
        binding[1],
        "python-module-binding",
      );
    }
  }
}

function tsJsFacts(
  line: string,
  lineNumber: number,
  importFacts: RayLineFact[],
  symbolFacts: RayLineFact[],
) {
  const trimmed = line.trim();

  const importMatch = trimmed.match(
    /^import(?:\s+type)?\s+.*?\s+from\s+["']([^"']+)["']/,
  );
  if (importMatch) {
    pushImport(
      importFacts,
      line,
      lineNumber,
      importMatch[1],
      "esm-import",
    );
  } else {
    const sideEffectImport = trimmed.match(/^import\s+["']([^"']+)["']/);
    if (sideEffectImport) {
      pushImport(
        importFacts,
        line,
        lineNumber,
        sideEffectImport[1],
        "esm-side-effect-import",
      );
    }

    const requireMatch = trimmed.match(/require\s*\(\s*["']([^"']+)["']\s*\)/);
    if (requireMatch) {
      pushImport(
        importFacts,
        line,
        lineNumber,
        requireMatch[1],
        "commonjs-require",
      );
    }
  }

  const exported = /^(?:export\s+(?:default\s+)?)?/.test(trimmed);
  const exportPrefix = /^export\b/.test(trimmed) ? "exported-" : "";

  const declaration = trimmed.match(
    /^(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(/,
  );
  if (declaration) {
    const name = declaration[1];
    let kind = `${exportPrefix}${/\basync\s+function\b/.test(trimmed) ? "async-function" : "function"}`;
    if (/^use[A-Z0-9_]/.test(name)) kind = `${exportPrefix}react-hook-candidate`;
    else if (/^[A-Z][A-Za-z0-9_$]*$/.test(name)) kind = `${exportPrefix}react-component-candidate`;
    else if (/^(?:on|handle)[A-Z0-9_]/.test(name)) kind = `${exportPrefix}event-handler-candidate`;
    pushSymbol(symbolFacts, line, lineNumber, name, kind);
    return;
  }

  const classMatch = trimmed.match(
    /^(?:export\s+(?:default\s+)?)?class\s+([A-Za-z_$][\w$]*)/,
  );
  if (classMatch) {
    pushSymbol(
      symbolFacts,
      line,
      lineNumber,
      classMatch[1],
      `${exportPrefix}class`,
    );
    return;
  }

  const interfaceMatch = trimmed.match(
    /^(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)/,
  );
  if (interfaceMatch) {
    pushSymbol(
      symbolFacts,
      line,
      lineNumber,
      interfaceMatch[1],
      `${exportPrefix}interface`,
    );
    return;
  }

  const typeMatch = trimmed.match(
    /^(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\b/,
  );
  if (typeMatch) {
    pushSymbol(
      symbolFacts,
      line,
      lineNumber,
      typeMatch[1],
      `${exportPrefix}type`,
    );
    return;
  }

  const enumMatch = trimmed.match(
    /^(?:export\s+)?enum\s+([A-Za-z_$][\w$]*)\b/,
  );
  if (enumMatch) {
    pushSymbol(
      symbolFacts,
      line,
      lineNumber,
      enumMatch[1],
      `${exportPrefix}enum`,
    );
    return;
  }

  const binding = trimmed.match(
    /^(?:export\s+)?(const|let|var)\s+([A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(.*)$/,
  );
  if (binding) {
    const bindingKind = binding[1];
    const name = binding[2];
    const rhs = binding[3];
    let kind = `${exportPrefix}${bindingKind}-binding`;

    if (/=>/.test(rhs) || /^(?:async\s*)?\(/.test(rhs)) {
      kind = `${exportPrefix}arrow-function`;
      if (/^use[A-Z0-9_]/.test(name)) kind = `${exportPrefix}react-hook-candidate`;
      else if (/^[A-Z][A-Za-z0-9_$]*$/.test(name)) kind = `${exportPrefix}react-component-candidate`;
      else if (/^(?:on|handle)[A-Z0-9_]/.test(name)) kind = `${exportPrefix}event-handler-candidate`;
    }

    pushSymbol(symbolFacts, line, lineNumber, name, kind);
  }

  void exported;
}

function rustFacts(
  line: string,
  lineNumber: number,
  importFacts: RayLineFact[],
  symbolFacts: RayLineFact[],
) {
  const trimmed = line.trim();

  const useMatch = trimmed.match(/^(?:pub\s+)?use\s+([^;]+)/);
  if (useMatch) {
    pushImport(
      importFacts,
      line,
      lineNumber,
      useMatch[1].trim(),
      "rust-use",
    );
  }

  const modMatch = trimmed.match(/^(?:pub\s+)?mod\s+([A-Za-z_]\w*)/);
  if (modMatch) {
    pushImport(
      importFacts,
      line,
      lineNumber,
      modMatch[1],
      "rust-mod",
    );
  }

  const patterns: readonly [RegExp, string][] = [
    [/^(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+([A-Za-z_]\w*)/, "rust-function"],
    [/^(?:pub(?:\([^)]*\))?\s+)?struct\s+([A-Za-z_]\w*)/, "rust-struct"],
    [/^(?:pub(?:\([^)]*\))?\s+)?enum\s+([A-Za-z_]\w*)/, "rust-enum"],
    [/^(?:pub(?:\([^)]*\))?\s+)?trait\s+([A-Za-z_]\w*)/, "rust-trait"],
    [/^(?:pub(?:\([^)]*\))?\s+)?const\s+([A-Za-z_]\w*)/, "rust-const"],
    [/^(?:pub(?:\([^)]*\))?\s+)?static\s+([A-Za-z_]\w*)/, "rust-static"],
  ];

  for (const [pattern, kind] of patterns) {
    const match = trimmed.match(pattern);
    if (match) {
      pushSymbol(symbolFacts, line, lineNumber, match[1], kind);
      break;
    }
  }
}

export function inspectLexically(source: RayFileContent | null): RayLexicalFacts {
  if (!source) {
    return {
      imports: [],
      symbols: [],
      importFacts: [],
      symbolFacts: [],
      todoLines: [],
      eventLines: [],
      directDomMutationLines: [],
      cssFixedLines: [],
      cssZIndexLines: [],
      todoCount: 0,
      eventBindingCount: 0,
      directDomMutationCount: 0,
      cssFixedCount: 0,
      cssZIndexCount: 0,
    };
  }

  const language = languageFor(source);
  const lines = source.content.split(/\r?\n/);
  const importFacts: RayLineFact[] = [];
  const symbolFacts: RayLineFact[] = [];
  const todoLines: number[] = [];
  const eventLines: number[] = [];
  const directDomMutationLines: number[] = [];
  const cssFixedLines: number[] = [];
  const cssZIndexLines: number[] = [];

  lines.forEach((line, lineIndex) => {
    const lineNumber = lineIndex + 1;

    if (language === "python") {
      pythonFacts(line, lineNumber, importFacts, symbolFacts);
    } else if (language === "typescript" || language === "javascript") {
      tsJsFacts(line, lineNumber, importFacts, symbolFacts);
    } else if (language === "rust") {
      rustFacts(line, lineNumber, importFacts, symbolFacts);
    }

    if (/\b(?:TODO|FIXME|HACK)\b/i.test(line)) todoLines.push(lineNumber);

    if (
      /\b(?:addEventListener|onClick|onChange|onInput|onSubmit|onContextMenu|onKeyDown|onKeyUp|onPointerDown|onPointerUp)\b/.test(
        line,
      )
    ) {
      eventLines.push(lineNumber);
    }

    if (
      /\.(?:appendChild|removeChild|insertBefore|replaceChild)\s*\(/.test(line)
    ) {
      directDomMutationLines.push(lineNumber);
    }

    if (/\bposition\s*:\s*fixed\b/i.test(line)) cssFixedLines.push(lineNumber);
    if (/\bz-index\s*:/i.test(line)) cssZIndexLines.push(lineNumber);
  });

  const boundedImports = importFacts.slice(0, 160);
  const boundedSymbols = symbolFacts.slice(0, 320);

  return {
    imports: unique(
      boundedImports.map((fact) => fact.evidence),
      80,
    ),
    symbols: unique(
      boundedSymbols.map((fact) => fact.name),
      120,
    ),
    importFacts: boundedImports,
    symbolFacts: boundedSymbols,
    todoLines: uniqueNumbers(todoLines, 160),
    eventLines: uniqueNumbers(eventLines, 200),
    directDomMutationLines: uniqueNumbers(directDomMutationLines, 160),
    cssFixedLines: uniqueNumbers(cssFixedLines, 160),
    cssZIndexLines: uniqueNumbers(cssZIndexLines, 160),
    todoCount: todoLines.length,
    eventBindingCount: eventLines.length,
    directDomMutationCount: directDomMutationLines.length,
    cssFixedCount: cssFixedLines.length,
    cssZIndexCount: cssZIndexLines.length,
  };
}

export function buildFindings(
  source: RayFileContent | null,
  facts: RayLexicalFacts,
  mode: RayMode,
): readonly RayFinding[] {
  if (!source || mode === "IDLE") return [];

  const firstImport = facts.importFacts[0];
  const firstSymbol = facts.symbolFacts[0];

  const findings: RayFinding[] = [
    {
      id: "read",
      severity: "PASS",
      title: "File content is visible to RAY",
      evidence: `${source.lineCount} lines / ${source.sizeBytes} bytes / ${source.encoding}${source.truncated ? " / preview truncated" : ""}`,
      source: source.relativePath,
      confidence: 1,
      lineStart: 1,
      factKind: "file-sight",
    },
    {
      id: "imports",
      severity: "INFO",
      title: "Language-aware dependency clues extracted",
      evidence: `${facts.importFacts.length} dependency clue(s) with source line coordinates.`,
      source: source.relativePath,
      confidence: 0.97,
      lineStart: firstImport?.line,
      factKind: "dependency",
    },
    {
      id: "symbols",
      severity: "INFO",
      title: "Language-aware symbols / bindings extracted",
      evidence: `${facts.symbolFacts.length} symbol or binding occurrence(s) with line/column coordinates.`,
      source: source.relativePath,
      confidence: 0.96,
      lineStart: firstSymbol?.line,
      factKind: "symbol",
    },
  ];

  if (facts.todoCount > 0) {
    findings.push({
      id: "todo",
      severity: "ATTENTION",
      title: "Unresolved source markers present",
      evidence: `${facts.todoCount} TODO/FIXME/HACK marker(s); first at L${facts.todoLines[0]}.`,
      source: source.relativePath,
      confidence: 0.99,
      lineStart: facts.todoLines[0],
      factKind: "todo",
    });
  }

  if (mode === "DEEP") {
    findings.push({
      id: "dom",
      severity: facts.directDomMutationCount > 0 ? "ATTENTION" : "PASS",
      title: "Direct DOM mutation lens",
      evidence:
        facts.directDomMutationCount > 0
          ? `${facts.directDomMutationCount} imperative DOM mutation call(s); first at L${facts.directDomMutationLines[0]}.`
          : "No appendChild/removeChild/insertBefore/replaceChild calls detected in this file.",
      source: source.relativePath,
      confidence: 0.99,
      lineStart: facts.directDomMutationLines[0],
      factKind: "dom-mutation",
    });

    findings.push({
      id: "events",
      severity: "INFO",
      title: "Event binding surface",
      evidence:
        facts.eventBindingCount > 0
          ? `${facts.eventBindingCount} event-binding token(s); first at L${facts.eventLines[0]}.`
          : "No tracked event-binding token detected.",
      source: source.relativePath,
      confidence: 0.92,
      lineStart: facts.eventLines[0],
      factKind: "event",
    });

    if (facts.cssFixedCount > 0 || facts.cssZIndexCount > 0) {
      const line = facts.cssFixedLines[0] ?? facts.cssZIndexLines[0];
      findings.push({
        id: "stacking",
        severity: "ATTENTION",
        title: "CSS stacking-context clues present",
        evidence: `position:fixed=${facts.cssFixedCount}, z-index declarations=${facts.cssZIndexCount}; first clue at L${line}.`,
        source: source.relativePath,
        confidence: 0.96,
        lineStart: line,
        factKind: "css-stacking",
      });
    }
  }

  return findings;
}
