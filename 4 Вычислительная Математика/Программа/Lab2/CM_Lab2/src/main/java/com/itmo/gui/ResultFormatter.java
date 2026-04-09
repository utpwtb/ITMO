package com.itmo.gui;

public final class ResultFormatter {

    private ResultFormatter() {}

    public static class Builder {
        private final StringBuilder sb = new StringBuilder();

        public Builder title(String text) {
            sb.append("═══════════════════════════════════════════════════════════\n");
            sb.append(text.toUpperCase());
            sb.append("\n═══════════════════════════════════════════════════════════\n\n");
            return this;
        }

        public Builder section(int num, String title) {
            sb.append(num).append(". ").append(title).append("\n");
            sb.append("───────────────────────────────────────────────────────────\n");
            return this;
        }

        public Builder section(String title) {
            sb.append(title).append("\n");
            sb.append("───────────────────────────────────────────────────────────\n");
            return this;
        }

        public Builder line(String format, Object... args) {
            sb.append("  ").append(String.format(format, args)).append("\n");
            return this;
        }

        public Builder line(String text) {
            sb.append("  ").append(text).append("\n");
            return this;
        }

        public Builder blank() {
            sb.append("\n");
            return this;
        }

        public Builder error(String msg) {
            sb.append("ОШИБКА: ").append(msg).append("\n");
            return this;
        }

        public Builder successCheck(boolean pass, String label) {
            sb.append("  ").append(label).append(": ").append(pass ? "Да ✓" : "Нет ✗").append("\n");
            return this;
        }

        public Builder checkResult(String label, double value, double epsilon) {
            boolean ok = Math.abs(value) < epsilon;
            line("%s = %.10f", label, value);
            line("  %s < %s: %s", label, epsilon, ok ? "Да ✓" : "Нет ✗");
            return this;
        }

        public Builder subSection(String text) {
            sb.append("  ").append(text).append("\n\n");
            return this;
        }

        public Builder raw(String text) {
            sb.append(text);
            return this;
        }

        public String build() {
            sb.append("\n═══════════════════════════════════════════════════════════\n");
            return sb.toString();
        }

        @Override
        public String toString() {
            return sb.toString();
        }
    }

    public static Builder builder() {
        return new Builder();
    }
}
