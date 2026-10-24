# Hilfsfunktionen zur Berechnung von Impedanzen mithilfe von objektorientierter Programmierung, weil ich meine begrenzte Zeit auf diesem Planeten offenbar nicht zu schätzen weiß...

from abc import ABC, abstractmethod
import numpy as np
import matplotlib.pyplot as plt

class FrequencyResponse(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def calc(self, f):
        ...


    # Bode-Diagramm

    @staticmethod
    def in_dB(values: np.ndarray, factor: int = 20):
        """
        values: Komplexe Werte (np.ndarray)
        factor: Skalarer Faktor zur Berechnung des dB Wertes: Spannung/Impedanz/... = 20, Leistung = 10 (default: 20)
        """
        return factor * np.log10(np.abs(values))
        
    
    def _plot_bode(self, f: np.ndarray, values: np.ndarray, symbol: str, unit: str = '', dB: bool = False):
        """
        f: Frequenzen in Hz (np.ndarray)
        values: Komplexe Werte (np.ndarray)
        symbol: Formelzeichen der komplexen Größe
        unit: Einheit der komplexen Größe
        """
        if unit == '' and dB == True:
            ylabel = f'|{symbol}(f)| in dB'
        elif dB == True:
            ylabel = f'|{symbol}(f)| in dB{unit}'
        else:
            ylabel = f'|{symbol}(f)| in {unit}'
        
        fig, (ax_mag, ax_phase) = plt.subplots(2, 1, sharex=True)
        fig.suptitle(self.name)
        if dB:
            ax_mag.semilogx(f, self.in_dB(values), label=f'|{symbol}(f)|')

        else:
            ax_mag.loglog(f, np.abs(values), label=f'|{symbol}(f)|')
        ax_mag.set_ylabel(ylabel)
        ax_mag.grid(True, which='both')
        ax_mag.legend()
    
        ax_phase.semilogx(f, np.angle(values, deg=True), label=rf'$\varphi_{symbol}(f)$')
        ax_phase.set_xlabel('f in Hz')
        ax_phase.set_ylabel(rf'$\varphi_{symbol}(f)$ in °')
        ax_phase.grid(True, which='both')
        ax_phase.legend()


    # Ortskurve

    
    def _plot_nyquist(self, f: np.ndarray, values: np.ndarray, symbol: str, unit: str):
        """
        f: Frequenzen in Hz (np.ndarray)
        values: Komplexe Werte (np.ndarray)
        symbol: Formelzeichen der komplexen Größe
        unit: Einheit der komplexen Größe
        """
        fig, ax = plt.subplots()
        fig.suptitle(self.name)

        ax.plot(values.real, values.imag, label=rf'$\underline{{{symbol}}}$(f)')
        ax.plot(values[0].real, values[0].imag,'o', label=rf'$\underline{{{symbol}}}$({f[0]:.3g} Hz) = ({values[0]:.3g}) {unit}')
        ax.set_xlabel(f'Re{{{symbol}}} in {unit}')
        ax.set_ylabel(f'Im{{{symbol}}} in {unit}')
        ax.set_aspect('equal')
        ax.grid(True, which='both')
        ax.legend()


# Impedanz

        
class Impedance(FrequencyResponse):    
    def calc_y(self, f):
        """f: Frequenzen in Hz (np.ndarray) -> Y(f): komplexes Array, gleiche Form wie f"""
        return 1 / self.calc(f)

    def plot_bode_z(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        self._plot_bode(f, self.calc(f), 'Z', unit='Ω', dB=False)
        
    def plot_bode_y(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        self._plot_bode(f, self.calc_y(f), 'Y', unit='S', dB=False)

    def plot_nyquist_z(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        self._plot_nyquist(f, self.calc(f), 'Z', unit='Ω')
        
    def plot_nyquist_y(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        self._plot_nyquist(f, self.calc_y(f), 'Y', unit='S')


# Widerstand, Induktivität, Kapazität

        
class BasicImpedance(Impedance):
    def __init__(self, component_value: float, component_label: str = ''):
        """
        component_value: Resistanz [R] = Ω, Induktivität [L] = H, Kapazität [C] = F 
        component_label: Bezeichnung bzw. Index der Resistanz / Induktivität / Kapazität
        """
        self.component_value = component_value
        self.component_label = component_label
        super().__init__(self._render_name())

    def _render_name(self):
        return rf'{self.component_symbol}$_{{\mathrm{{{self.component_label}}}}}$[{self.component_value} {self.component_unit}]'
        
class Resistance(BasicImpedance):
    component_symbol = 'R'
    component_unit = 'Ω'
    
    def calc(self, f):
        """f: Frequenzen in Hz (np.ndarray) -> Z(f): komplexes Array, gleiche Form wie f"""
        return np.full(np.shape(f),self.component_value, dtype=np.cdouble)

class Inductance(BasicImpedance):
    component_symbol = 'L'
    component_unit = 'H'

    def calc(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        w = 2 * np.pi * f
        return 1j * w * self.component_value

class Capacitance(BasicImpedance):
    component_symbol = 'C'
    component_unit = 'F'

    def calc(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        w = 2 * np.pi * f
        return 1 / (1j * w * self.component_value)


# Reihen und Parallelschaltung:

        
class CompositeImpedance(Impedance):
    def __init__(self, *impedances):
        self.impedances = impedances
        super().__init__(self._concat_names())
        
    def _concat_names(self):
        names = []
        for impedance in self.impedances:
            names.append(impedance.name)
        name = self.layout_operator.join(names) 
        return f'( {name} )'


class SeriesImpedance(CompositeImpedance):
    layout_operator = ' + '
    def calc(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        z = 0
        for impedance in self.impedances:
            z += impedance.calc(f)
        return z


class ParallelImpedance(CompositeImpedance):
    layout_operator = ' || '
    def calc(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        y = 0
        for impedance in self.impedances:
            y += impedance.calc_y(f)
        z = 1/y
        return z


class VoltageDivider(FrequencyResponse):
    def __init__(self, divider_name, Z_1: Impedance, Z_2: Impedance):
        """
        Z_1: Erste Impedanz – Über sie fällt ein Teil der Eingangsspannung ab
        Z_2: Zweite Impedanz – Hier liegt die Ausgansspannung an
        
        o––––––[Z_1]––––––o––––––o
                          |
        U_e              [Z_2]  U_a
                          |
        o–––––––––––––––––o––––––o
        """
        self.divider_name = divider_name 
        self.Z_1 = Z_1
        self.Z_2 = Z_2
        super().__init__(self._render_name())
        
    def _render_name(self):
        return rf'{self.divider_name}[{self.Z_1.name}, {self.Z_2.name}]'

    def calc(self, f):
        return self.Z_2.calc(f) / (self.Z_1.calc(f) + self.Z_2.calc(f))

    def plot_bode(self, f):
        """f: Frequenzen in Hz (np.ndarray)"""
        self._plot_bode(f, self.calc(f), 'G', unit = '', dB=True)

# Dass ich meine begrenzte Zeit auf diesem Planeten nicht zu schätzen weiß, war noch maßlos untertrieben.