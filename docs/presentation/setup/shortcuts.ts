import type { NavOperations, ShortcutOptions } from '@slidev/types'

export default function (_nav: NavOperations, shortcuts: ShortcutOptions[]) {
  // Remove the goto shortcut — the G key accidentally opens a full slide
  // index overlay (Goto dialog) that's hard to dismiss. Use the overview
  // (O key) for slide navigation instead.
  return shortcuts.filter(s => s.name !== 'goto')
}
