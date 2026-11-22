package org.nx2a;

/** Use the same language as the in-game overlay, not the language of arbitrary guest strings. */
final class UiLocale {
    static { System.loadLibrary("dmhost"); }

    private UiLocale() {}

    static native boolean chinese();

    static String text(String english, String simplified) {
        return chinese() ? simplified : english;
    }
}
