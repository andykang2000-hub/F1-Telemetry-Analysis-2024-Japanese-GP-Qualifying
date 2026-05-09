"""
F1 Telemetry Analysis — 2024 Japanese GP Qualifying
VER vs HAM | Suzuka Circuit

Author : Yoon
Data   : FastF1 (https://github.com/theOehrly/Fast-F1)
Output : outputs/japan_gp_qualifying_VER_HAM_final.png
"""

import os
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec
from fastf1.plotting import get_driver_color

# ── Cache & session ───────────────────────────────────────────────────────────
os.makedirs('f1_cache', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

fastf1.Cache.enable_cache('f1_cache')
session = fastf1.get_session(2024, 'Japan', 'Q')
session.load()

# ── Driver laps ───────────────────────────────────────────────────────────────
ver_lap = session.laps.pick_drivers('VER').pick_fastest()
ham_lap = session.laps.pick_drivers('HAM').pick_fastest()

ver_color = '#1E41FF'   # Red Bull blue
ham_color = '#008F84'   # Mercedes teal (darkened for white background)

# ── Telemetry + position data ─────────────────────────────────────────────────
ver_tel = ver_lap.get_telemetry(frequency='original').add_distance()
ver_tel = ver_tel.merge_channels(ver_lap.get_pos_data())

ham_tel = ham_lap.get_telemetry(frequency='original').add_distance()
ham_tel = ham_tel.merge_channels(ham_lap.get_pos_data())

# ── Time delta ────────────────────────────────────────────────────────────────
delta_time, ref_tel, compare_tel = fastf1.utils.delta_time(ver_lap, ham_lap)

# ── Sector times ──────────────────────────────────────────────────────────────
def fmt_sector(td):
    return f'{td.total_seconds():.3f}s'

ver_s1 = fmt_sector(ver_lap['Sector1Time'])
ver_s2 = fmt_sector(ver_lap['Sector2Time'])
ver_s3 = fmt_sector(ver_lap['Sector3Time'])
ham_s1 = fmt_sector(ham_lap['Sector1Time'])
ham_s2 = fmt_sector(ham_lap['Sector2Time'])
ham_s3 = fmt_sector(ham_lap['Sector3Time'])

# ── Suzuka corner annotations (approx. distance in metres) ───────────────────
corners = {
    'T1':       150,
    'Esses':    600,
    'Dunlop':   900,
    'Degner 1': 1250,
    'Degner 2': 1450,
    'Hairpin':  1750,
    'Spoon':    2700,
    '130R':     3700,
    'Chicane':  4000,
}

# ── Sector boundaries & colors ────────────────────────────────────────────────
sector_boundaries = {
    'S1': (0, 1900),
    'S2': (1900, 3400),
    'S3': (3400, ver_tel['Distance'].max()),
}
sector_colors = {'S1': '#e63946', 'S2': '#457b9d', 'S3': '#2a9d8f'}

# ── Style constants ───────────────────────────────────────────────────────────
BG   = '#ffffff'
GRID = '#dddddd'
TEXT = '#111111'

# ── Circuit map helpers ───────────────────────────────────────────────────────
def draw_speed_map(ax, tel, driver_label):
    x, y  = tel['X'].values, tel['Y'].values
    speed = tel['Speed'].values

    points   = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    norm = plt.Normalize(speed.min(), speed.max())
    lc   = LineCollection(segments, cmap='plasma', norm=norm, linewidth=2)
    lc.set_array(speed)
    ax.add_collection(lc)

    brake_mask = tel['Brake'].astype(bool).values
    ax.scatter(x[brake_mask], y[brake_mask],
               color='red', s=2, zorder=5, label='Braking')

    ax.autoscale_view()
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor(BG)
    ax.set_title(f'{driver_label} — Speed + Braking Zones',
                 color=TEXT, fontsize=9, pad=4)
    ax.legend(loc='lower right', fontsize=7, markerscale=4,
              facecolor=BG, labelcolor=TEXT, framealpha=0.5)
    return lc


def draw_delta_map(ax, tel, delta_time):
    x, y     = tel['X'].values, tel['Y'].values
    tel_dist = tel['Distance'].values

    delta_dist   = np.linspace(tel_dist.min(), tel_dist.max(), len(delta_time))
    delta_interp = np.interp(tel_dist, delta_dist, delta_time)

    points   = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    abs_max = np.abs(delta_interp).max()
    norm    = plt.Normalize(-abs_max, abs_max)
    lc      = LineCollection(segments, cmap='RdYlGn', norm=norm, linewidth=2.5)
    lc.set_array(delta_interp[:-1])
    ax.add_collection(lc)

    ax.autoscale_view()
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor(BG)
    ax.set_title('Time Delta  (Green = VER ahead · Red = HAM ahead)',
                 color=TEXT, fontsize=9, pad=4)
    return lc


# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 26), facecolor=BG)
fig.suptitle(
    '2024 Japanese GP Qualifying — VER vs HAM\nTelemetry Analysis · Suzuka Circuit',
    color=TEXT, fontsize=15, y=0.995, linespacing=1.6
)

gs = GridSpec(
    7, 3, figure=fig,
    height_ratios=[2.2, 0.08, 1.2, 1, 1, 1, 0.05],
    hspace=0.55, wspace=0.25
)

# ── Circuit maps ──────────────────────────────────────────────────────────────
ax_ver_map   = fig.add_subplot(gs[0, 0])
ax_ham_map   = fig.add_subplot(gs[0, 1])
ax_delta_map = fig.add_subplot(gs[0, 2])

lc_ver   = draw_speed_map(ax_ver_map,   ver_tel, 'VER')
lc_ham   = draw_speed_map(ax_ham_map,   ham_tel, 'HAM')
lc_delta = draw_delta_map(ax_delta_map, ver_tel, delta_time)

# Colorbars
cbar_ver   = fig.add_subplot(gs[1, 0])
cbar_ham   = fig.add_subplot(gs[1, 1])
cbar_delta = fig.add_subplot(gs[1, 2])

fig.colorbar(lc_ver, cax=cbar_ver, orientation='horizontal').set_label('Speed (km/h)', color=TEXT, fontsize=8)
fig.colorbar(lc_ham, cax=cbar_ham, orientation='horizontal').set_label('Speed (km/h)', color=TEXT, fontsize=8)
cb = fig.colorbar(lc_delta, cax=cbar_delta, orientation='horizontal')
cb.set_label('Δ Time (s)  +VER / −HAM', color=TEXT, fontsize=8)

for cax in [cbar_ver, cbar_ham, cbar_delta]:
    cax.tick_params(colors=TEXT, labelsize=7)

# ── Telemetry panels ──────────────────────────────────────────────────────────
ax_speed    = fig.add_subplot(gs[2, :])
ax_throttle = fig.add_subplot(gs[3, :])
ax_brake    = fig.add_subplot(gs[4, :])
ax_delta_t  = fig.add_subplot(gs[5, :])

channels = [
    (ax_speed,    'Speed',    'Speed (km/h)'),
    (ax_throttle, 'Throttle', 'Throttle (%)'),
    (ax_brake,    'Brake',    'Brake'),
]

for ax, channel, ylabel in channels:
    ax.set_facecolor(BG)

    for sector, (s_start, s_end) in sector_boundaries.items():
        ax.axvspan(s_start, s_end, alpha=0.07,
                   color=sector_colors[sector], zorder=0)

    data_ver = ver_tel[channel] if channel != 'Brake' else ver_tel[channel].astype(int)
    data_ham = ham_tel[channel] if channel != 'Brake' else ham_tel[channel].astype(int)

    ax.plot(ver_tel['Distance'], data_ver,
            color=ver_color, label='VER', linewidth=1.3, zorder=3)
    ax.plot(ham_tel['Distance'], data_ham,
            color=ham_color, label='HAM', linewidth=1.3, alpha=0.85, zorder=3)

    ax.set_ylabel(ylabel, color=TEXT, fontsize=9)
    ax.tick_params(colors=TEXT, labelsize=8)
    ax.legend(facecolor=BG, labelcolor=TEXT, fontsize=8, loc='upper right')
    ax.grid(axis='y', color=GRID, linewidth=0.5, linestyle='--')
    for spine in ax.spines.values():
        spine.set_color(GRID)

    # Corner annotations on speed panel only
    if channel == 'Speed':
        for name, dist in corners.items():
            ax.axvline(dist, color='#999999', linewidth=0.4,
                       linestyle=':', alpha=0.6, zorder=2)
            ax.text(dist, 50, name, color='#888888', fontsize=6.5,
                    rotation=90, va='bottom', ha='right', alpha=0.85)

# ── Sector time banner ────────────────────────────────────────────────────────
for sector, (s_start, s_end) in sector_boundaries.items():
    mid   = (s_start + s_end) / 2
    color = sector_colors[sector]
    ver_t = {'S1': ver_s1, 'S2': ver_s2, 'S3': ver_s3}[sector]
    ham_t = {'S1': ham_s1, 'S2': ham_s2, 'S3': ham_s3}[sector]

    ax_speed.text(mid, 1.18, sector,
                  transform=ax_speed.get_xaxis_transform(),
                  color=color, fontsize=9, fontweight='bold',
                  ha='center', va='bottom')
    ax_speed.text(mid, 1.11, f'VER  {ver_t}',
                  transform=ax_speed.get_xaxis_transform(),
                  color=ver_color, fontsize=7.5, ha='center', va='bottom')
    ax_speed.text(mid, 1.05, f'HAM  {ham_t}',
                  transform=ax_speed.get_xaxis_transform(),
                  color=ham_color, fontsize=7.5, ha='center', va='bottom')

# ── Time delta panel ──────────────────────────────────────────────────────────
ax_delta_t.set_facecolor(BG)

for sector, (s_start, s_end) in sector_boundaries.items():
    ax_delta_t.axvspan(s_start, s_end, alpha=0.07,
                       color=sector_colors[sector], zorder=0)

ax_delta_t.plot(ref_tel['Distance'], delta_time,
                color=TEXT, linewidth=1, zorder=4)
ax_delta_t.axhline(0, color='#aaaaaa', linewidth=0.6, linestyle='--')
ax_delta_t.fill_between(ref_tel['Distance'], delta_time, 0,
                         where=(delta_time > 0),
                         color=ver_color, alpha=0.35, label='VER ahead', zorder=3)
ax_delta_t.fill_between(ref_tel['Distance'], delta_time, 0,
                         where=(delta_time < 0),
                         color=ham_color, alpha=0.35, label='HAM ahead', zorder=3)

ax_delta_t.set_ylabel('Δ Time (s)', color=TEXT, fontsize=9)
ax_delta_t.set_xlabel('Distance (m)', color=TEXT, fontsize=9)
ax_delta_t.tick_params(colors=TEXT, labelsize=8)
ax_delta_t.legend(facecolor=BG, labelcolor=TEXT, fontsize=8, loc='upper left')
ax_delta_t.grid(axis='y', color=GRID, linewidth=0.5, linestyle='--')
for spine in ax_delta_t.spines.values():
    spine.set_color(GRID)

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = 'outputs/japan_gp_qualifying_VER_HAM_final.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=BG)
plt.show()
print(f"Saved: {out_path}")
