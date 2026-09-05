import type { CanonicalConcept } from "./models";

export const CANONICAL_SEED: readonly CanonicalConcept[] = [
  {
    id: "llm-cartridge-bay",
    formalName: "LLM Cartridge Bay",
    abbreviation: "LLCB",
    status: "ADOPTED",
    importance: "CRITICAL",
    scope: "VERTEX_BRAIN_SYSTEM",
    category: "LLM_INFRASTRUCTURE",
    summary:
      "Vertex Brain Systemに既存LLMや将来のTeacher Modelを差し込むためのモデル非依存カートリッジ導入口。",
    functionText:
      "Model RuntimeとBrain Systemの境界を安定させ、モデル交換可能性を確保する。",
    description:
      "LLMそのものをWorkstationやBrainの所有物にせず、交換可能なCartridgeとして扱う。",
    origin:
      "複数LLM・Teacher Model・ローカルモデルを切り替える設計議論から採用。",
    aliases: "LLM Bay, Cartridge Bay",
    related: "Vertex Brain System",
    flavorBadge: "超採用！",
    adoptedBy: "Human + Vera",
    notes: "",
  },
  {
    id: "vertex-canonical-registry",
    formalName: "Vertex Canonical Registry",
    abbreviation: "VCR",
    status: "ADOPTED",
    importance: "CRITICAL",
    scope: "ALL_VERTEX_PRODUCTS",
    category: "REGISTRY",
    summary:
      "Vertex固有の正式名称・略称・意味・由来をカードとして永続化する共通レジストリ。",
    functionText:
      "HumanとAIが同じ概念を同じCanonical IDで参照できるようにする。",
    description:
      "製品や会話をまたいでVertex固有概念の意味を固定し、表記揺れと意味の漂流を抑える。",
    origin:
      "雑談から大量に生まれるVertex固有語彙を正式資産として残す必要から採用。",
    aliases: "Canonical Registry",
    related: "Vertex Language Layer",
    flavorBadge: "超採用！",
    adoptedBy: "Human + Vera",
    notes: "",
  },
  {
    id: "vertex-gauge",
    formalName: "Vertex Gauge",
    abbreviation: "VGAUGE",
    status: "STABLE",
    importance: "IMPORTANT",
    scope: "VERTEX_WORKSTATION",
    category: "MEASUREMENT",
    summary:
      "Vertex Works / Workstationのデスクトップ計測施設。画面・ウィンドウ・UIの寸法、距離、余白、座標、DPI、モニター境界を実測しEvidenceへ接続する。",
    functionText:
      "UI/UX検証時に推測ではなく実測値をEvidenceとして返す。",
    description:
      "視覚調整を感覚だけに依存させず、寸法・座標・DPIを再現可能な証拠へ変える。",
    origin:
      "旧WorksでUI崩れの原因を画面実測する必要から構想。",
    aliases: "VGauge",
    related: "RAY",
    flavorBadge: "超採用！",
    adoptedBy: "Human + Vera",
    notes: "",
  },
  {
    id: "vertex-language-layer",
    formalName: "Vertex Language Layer",
    abbreviation: "VLL",
    status: "ADOPTED",
    importance: "CRITICAL",
    scope: "ALL_VERTEX_PRODUCTS",
    category: "LANGUAGE_INFRASTRUCTURE",
    summary:
      "Canonicalな機械意味とHuman向け言語・ノリ・ドメイン表現を分離する言語層。",
    functionText:
      "UIラベル、Canonical用語、説明、Flavor、Error文、Domain Language Packを製品共通で切り替える。",
    description:
      "ADOPTEDという意味を維持したまま「採用」「超採用！」「ADOPTED」など表示を切り替える。単なる翻訳ではなくHumanとVertex Worldの言語膜。",
    origin:
      "Canonical CardにHuman向け日本語と遊び表現を載せる必要から日本語化Languageが復活。",
    aliases: "Vertex Language, Language Layer",
    related: "Vertex Canonical Registry",
    flavorBadge: "日本語化、帰還www",
    adoptedBy: "Human + Vera",
    notes: "SemanticとFlavorを混ぜない。",
  },
  {
    id: "vertex-lifecycle-core",
    formalName: "Vertex Lifecycle Core",
    abbreviation: "VLC",
    status: "STABLE",
    importance: "IMPORTANT",
    scope: "ALL_VERTEX_PRODUCTS",
    category: "LIFECYCLE",
    summary:
      "全Vertex製品共通の更新・再起動・Release切替・Health Proof・Rollback基盤。",
    functionText:
      "配布・更新・検証・復旧を製品ごとの場当たり実装から切り離す。",
    description:
      "製品寿命全体を跨ぐ共通Lifecycle機構。",
    origin:
      "継続更新とRollbackを製品横断で統一する必要から採用。",
    aliases: "Lifecycle Core",
    related: "Vertex Runtime Factory",
    flavorBadge: "徹夜の更新地獄から超採用！",
    adoptedBy: "Human + Vera",
    notes: "",
  },
  {
    id: "vertex-native",
    formalName: "Vertex Native",
    abbreviation: "VXN",
    status: "ADOPTED",
    importance: "CRITICAL",
    scope: "ALL_VERTEX_PRODUCTS",
    category: "RUNTIME",
    summary:
      "Vertex Worldの独立神経基盤。AI/Agent/Tool/Runtime間の伝達を高密度・低摩擦で流すためのVertexネイティブ通信・表現・Flow Core。",
    functionText:
      "自然言語・GUI・音声・図と実行系をVertex Native表現へ変換して流す。",
    description:
      "特定言語や単一Runtimeへ依存しないVertex World内部の伝達層。",
    origin:
      "LLMが扱いやすい中間表現と実行神経系を作る構想から正式採用。",
    aliases: "VXN, Vertex Native Language",
    related: "ARD, Vertex Runtime Factory",
    flavorBadge: "超採用！",
    adoptedBy: "Human + Vera",
    notes: "",
  },
];
