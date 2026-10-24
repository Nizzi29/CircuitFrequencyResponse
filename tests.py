# KI-generierte Tests (Version mit Labels, aufrechte Indizes)
# Bezeichnungen wie im Versuchsskript: R_m, R_Ls, R_d, L_r/C_r (Reihenkreis), L_p/C_p (Parallelkreis)


# 1. Kontrollwerte (das Label darf die Rechnung nicht beeinflussen)

def pruefe(name, Z, soll):
    ok = np.isclose(Z[0], soll, rtol=1e-4)
    print(f"{'OK    ' if ok else 'FALSCH'} {name}: {Z[0]:.1f} Ω (soll {complex(soll):.1f} Ω)")

f = np.array([1000.0])
pruefe("Resistance mit Label", Resistance(2000, 'm').calc(f), 2000)
pruefe("Resistance ohne Label", Resistance(2000).calc(f), 2000)
pruefe("Inductance", Inductance(1, 'r').calc(f), 6283.19j)
pruefe("Capacitance", Capacitance(100e-9, 'r').calc(f), -1591.55j)
pruefe("SeriesImpedance", SeriesImpedance(Resistance(2000, 'm'), Resistance(35, 'Ls'), Inductance(1, 'r'),
                                          Capacitance(100e-9, 'r')).calc(f), 2035 + 4691.64j)
pruefe("ParallelImpedance @200 Hz", ParallelImpedance(Inductance(1, 'p'), Capacitance(440e-9, 'p'))
       .calc(np.array([200.0])), 4117.69j)


# 2. Namen als Text (print zeigt $...$ absichtlich unverändert)
#    Die Sollwerte passen zum Format X$_{\mathrm{label}}$[Wert Einheit].
#    r'...' (raw string), damit Python den Backslash in \mathrm nicht als Escape-Sequenz liest.

def pruefe_name(objekt, soll):
    ok = objekt.name == soll
    print(f"{'OK    ' if ok else 'FALSCH'} {objekt.name!r}" + ('' if ok else f"  (soll {soll!r})"))

print()
pruefe_name(Resistance(35, 'Ls'), r'R$_{\mathrm{Ls}}$[35 Ω]')
pruefe_name(Resistance(35), r'R$_{\mathrm{}}$[35 Ω]')
pruefe_name(Inductance(1, 'p'), r'L$_{\mathrm{p}}$[1 H]')
pruefe_name(Capacitance(440e-9, 'p'), r'C$_{\mathrm{p}}$[4.4e-07 F]')
pruefe_name(ParallelImpedance(SeriesImpedance(Resistance(35, 'Ls'), Inductance(1, 'p')), Capacitance(440e-9, 'p')),
            r'( ( R$_{\mathrm{Ls}}$[35 Ω] + L$_{\mathrm{p}}$[1 H] ) || C$_{\mathrm{p}}$[4.4e-07 F] )')


# 3. Randfälle

print()
try:
    print("Leere Schaltung:", SeriesImpedance().name)
except Exception as e:
    print("Leere Schaltung ->", type(e).__name__ + ":", e)

f0 = 1 / (2 * np.pi * np.sqrt(1 * 440e-9))
print(f"Ideales L || C bei f0 = {f0:.1f} Hz:",
      ParallelImpedance(Inductance(1, 'p'), Capacitance(440e-9, 'p')).calc(np.array([f0])))

# Zwischenklassen müssen abstrakt sein, sonst fehlt irgendwo calc
for klasse in (BasicImpedance, CompositeImpedance):
    try:
        klasse(1)
        print(f"FALSCH {klasse.__name__} lässt sich erzeugen")
    except TypeError:
        print(f"OK     {klasse.__name__} ist abstrakt")


# 4. Namensvorschau: so rendert matplotlib die Namen (Index tiefgestellt und aufrecht)

vorschau = [Resistance(2000, 'm'), Resistance(35, 'Ls'), Resistance(35), Inductance(1, 'r'), Capacitance(100e-9, 'r'),
            ParallelImpedance(SeriesImpedance(Resistance(35, 'Ls'), Inductance(1, 'p')), Capacitance(440e-9, 'p'))]
fig, ax = plt.subplots(figsize=(7, 3))
ax.axis('off')
for k, objekt in enumerate(vorschau):
    ax.text(0, 1 - k / len(vorschau), objekt.name, fontsize=12, va='top')
fig.suptitle('Namensvorschau')


# 5. Plots mit Labels

f = np.logspace(1, 4, 2000)

# 4.3 Parallelkreis mit realer Spule: Spitze bei ~240 Hz, Höhe ~ L / (R_Ls * C) ≈ 65 kΩ
zp = ParallelImpedance(SeriesImpedance(Resistance(35, 'Ls'), Inductance(1, 'p')), Capacitance(440e-9, 'p'))
zp.plot_bode_z(f)

# 4.2 Serienkreis: Admittanz-Ortskurve ist ein Kreis mit Durchmesser 1 / 2035 Ω ≈ 0,49 mS
zs = SeriesImpedance(Resistance(2000, 'm'), Resistance(35, 'Ls'), Inductance(1, 'r'), Capacitance(100e-9, 'r'))
zs.plot_nyquist_y(f)

RC_Filter =  VoltageDivider('RC-Filter', Resistance(1.59e3), Capacitance(100e-9))
RC_Filter.plot_bode(f)

plt.show()
