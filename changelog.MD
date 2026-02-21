# Changelog

All notable changes to this project will be documented in this file.

---

## [2.0.0] - 2026-02-21

### 💥 Breaking Changes

- Minimum Flet version bumped from `0.28.0` to `0.80.5`
- `ft.app()` replaced by `ft.run()` — the old entrypoint no longer exists
- `ft.border.only()` replaced by `ft.Border.only()` (deprecated since 0.80.0)
- `NotificationDemo` class removed — UI is now fully declarative

### ✨ Added

- **Declarative UI architecture** using `@ft.component` and `@ft.observable`
- `AppState` dataclass — single reactive state shared across all components, powered by `@ft.observable`
- `CounterBadge` component — isolated, auto-updating notification counter badge
- `AppBar` component — reactive app bar that re-renders on state changes
- `SimpleSection`, `ProgressSection`, `ButtonsSection`, `ImagesSection`, `TextSection`, `AdvancedSection` — each UI section is now its own self-contained component
- `_show_snack()` helper using `ft.context.page` instead of a stored page reference
- `_dev_simulate()` pure helper function — no longer tied to a class instance
- `page.render(App)` as the new app bootstrap method
- Docstrings on all public functions and classes in both `main.py` and `flet_notify.py`

### 🔄 Changed

- **State management**: `self.notification_count` + `ft.Ref` replaced by `AppState.notification_count` as observable state — counter updates propagate automatically with no manual `update()` calls
- **Page access**: `self.page` references replaced by `ft.context.page` throughout components
- **`android-notify`** bumped from `1.60.8.dev0` to `1.60.10`
- Theme and FAB setup moved inside the `App` component
- `_increment_counter()` method replaced by `state.increment()` on `AppState`
- All event handlers are now closures inside their respective components instead of class methods

### 🗑️ Removed

- `NotificationDemo` class and its `initialize()` method
- `counter_text_ref` (`ft.Ref[ft.Text]`) — no longer needed with reactive state
- Manual `page.update()` calls in most places — declarative re-renders handle it
- `_build_*` methods (`_build_app_bar`, `_build_simple_section`, etc.)
- All `page.add()` + `page.update()` imperative patterns at startup

### 🐛 Fixed

- `DeprecationWarning` for `ft.border.only()` — migrated to `ft.Border.only()`

---

## [1.0.0] - 2025-01-01

### ✨ Added

- Initial release
- `FletNotify` singleton manager with Android platform validation
- `NotificationBuilder` with fluent/chained API
- `FletNotification` with real-time update methods (`update_title`, `update_message`, `update_progress`, `remove_progress`, `cancel`, `refresh`)
- `NotificationStyle` enum — `SIMPLE`, `PROGRESS`, `INBOX`, `BIG_TEXT`, `LARGE_ICON`, `BIG_PICTURE`, `BOTH_IMAGES`
- `NotificationImportance` enum — `URGENT`, `HIGH`, `MEDIUM`, `LOW`, `NONE`
- Custom channel support via `FletNotify.create_channel()` and `delete_channel()`
- `check_permission()` and `request_permission()` for Android 13+ (SDK 33+)
- Developer mode — automatic simulation when running outside Android
- Complete demo app with all notification types covered
- Bilingual documentation (English + Portuguese)