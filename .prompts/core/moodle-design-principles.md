# Moodle Design Principles & Component Library Reference

This document provides a condensed reference for implementing UI features that align with Moodle's design standards and component library. Use this as your starting point, then access specific component pages as needed.

## Quick Reference: Core Principles

**Central Purpose:** The Moodle Component Library documents frequently used UI components to enable efficient, consistent interface development across the platform.

**Key Philosophy:** Developers should leverage existing documented components rather than creating custom solutions. This reduces redundancy, improves consistency, and enhances user experience.

**Design Foundation:**
- Bootstrap 5 components are included with every Moodle 5.x+ installation (with backwards compatibility for Bootstrap 4 syntax through Moodle 6.0)
- All components represent approved, safe building blocks for frontend development

**Bootstrap 5 Key Changes (Moodle 5.x+):**
- Class name updates: `.badge-*` → `.text-bg-*`, `.ml-*` → `.ms-*`, `.text-left` → `.text-start`, `.sr-only` → `.visually-hidden`
- Data attributes use namespacing: `data-toggle` → `data-bs-toggle`, `data-target` → `data-bs-target`
- jQuery removed from Bootstrap 5 (but Moodle provides compatibility layer through 6.0)
- Form classes updated: `.custom-select` → `.form-select`, `.custom-check` → `.form-check`

**Target Audience:** Designers, developers, and UX professionals creating core Moodle code or extensions.

---

## Complete Navigation Index

### Moodle Components (UI Building Blocks)
Each component has comprehensive documentation on usage, examples, and implementation details.

| Component | URL |
|-----------|-----|
| Activity Icons | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/activity-icons/ |
| Buttons | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/buttons/ |
| Course Cards | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/course-cards/ |
| Form Elements | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/form-elements/ |
| Footer | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/footer/ |
| Icons | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/icons/ |
| Notification Badges | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/notification-badges/ |
| Notifications | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/notifications/ |
| Toggle Input | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/toggle-input/ |
| Search Input | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/search-input/ |
| Show More | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/show-more/ |
| Collapsible Sections | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/collapsable-sections/ |
| Task Indicator | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/task-indicator/ |
| Action Menus | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/action-menus/ |
| Dropdowns | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/dropdowns/ |
| HTML Modals | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/html-modals/ |
| Dynamic Tabs | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/components/dynamic-tabs/ |

### JavaScript Functionality
Interactive utilities and data visualization components.

| Feature | URL |
|---------|-----|
| Confirm Dialog | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/javascript/confirm/ |
| Toast Notifications | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/javascript/toast/ |
| Emoji Picker | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/javascript/emojipicker/ |
| Sortable Lists | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/javascript/sortable-list/ |
| Moodle Charts | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/javascript/moodle-charts/ |

### Design Standards & Themes
Guidelines for colors, spacing, typography, layout, and visual hierarchy.

| Standard | URL |
|----------|-----|
| Colours | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/themes/colours/ |
| Grids | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/themes/grids/ |
| Positioning | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/themes/positioning/ |
| Spacing | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/themes/spacing/ |
| Icon Sizes | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/themes/icon-sizes/ |
| Layout | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/themes/layout/ |
| Text | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/themes/text/ |

### Accessibility Guidelines
Standards for accessible UI implementation.

| Guideline | URL |
|-----------|-----|
| Links | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/accessibility/links/ |
| Colour Contrast | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/accessibility/colour-contrast/ |
| Keyboard Access | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/accessibility/keyboard-access/ |

### Component Library Documentation
Internal reference for contributing to the library.

| Topic | URL |
|-------|-----|
| Getting Started | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/getting-started/ |
| Adding Pages | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/adding-pages/ |
| Adding Images | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/adding-images/ |
| Syntax Highlighting | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/syntax-highlighting/ |
| Component Library Backend | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/component-library-backend/ |
| Example Files | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/example-files/ |
| Moodle JavaScript | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/moodle-javascript/ |
| Moodle Templates | https://componentlibrary.moodle.com/admin/tool/componentlibrary/docspage.php/library/moodle-templates/ |

---

## Key Design Guidelines (Summary)

### Components to Use
When implementing UI features, prioritize these pre-built, tested components:

**Interactive Elements:** Buttons, toggles, dropdowns, modals, tabs, action menus
**Form Structures:** Standardized form inputs and elements
**Visual Indicators:** Badges, notifications, task indicators
**Navigation:** Action menus, collapsible sections
**Information Display:** Cards, footers, icons

### Design Standards to Follow

**Bootstrap Foundation:**
- All components are built on Bootstrap, which is included with every Moodle installation
- Refer to official Bootstrap documentation for additional component details
- Use Bootstrap utilities for layout, spacing, and responsive design

**Accessibility:**
- Ensure proper color contrast for readability
- Support keyboard navigation for all interactive elements
- Use semantic HTML and ARIA labels where appropriate
- Test components for accessibility compliance

**Visual Consistency:**
- Follow Moodle's color palette (see Colours standard)
- Use consistent spacing and grids (see Spacing & Grids standards)
- Maintain typographic hierarchy (see Text standard)
- Use consistent icon sizing (see Icon Sizes standard)
- Follow layout patterns (see Layout standard)

---

## For Agent Implementation

When implementing UI features for Moodle:

1. **Start here:** Review this document for core principles
2. **Check for existing components:** Search the Components section above
3. **Review design standards:** Consult the Themes section for visual guidelines
4. **Verify accessibility:** Check the Accessibility Guidelines section
5. **Access detailed docs:** Visit the component page URL for full documentation, examples, and code samples
6. **Use Bootstrap:** Leverage Bootstrap components as the foundation for any custom elements

---

## Bootstrap 5 Migration Reference

For detailed Bootstrap 5 migration guidance (class name changes, data attributes, SCSS functions, etc.), consult:
**https://moodledev.io/docs/5.0/guides/bs5migration**

Use this page if you encounter:
- Deprecated Bootstrap 4 class names in existing code
- Data attribute compatibility issues
- SCSS function updates needed (e.g., `theme-color-level()` → `shift-color()`)
- Form or badge component upgrades

---

## Additional Resources

- **Official Moodle Component Library:** https://componentlibrary.moodle.com/
- **Bootstrap 5 Documentation:** https://getbootstrap.com/docs/5.0/
- **Moodle Developer Documentation:** https://docs.moodle.org/
- **Bootstrap 5 Migration Guide:** https://moodledev.io/docs/5.0/guides/bs5migration

---

*This reference was created as a condensed guide for efficient UI development aligned with Moodle standards. For comprehensive examples, implementation details, and component previews, visit the full Moodle Component Library at the URLs listed above.*
