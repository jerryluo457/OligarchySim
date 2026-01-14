# app.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
from simulation import run_simulation
from metrics import eliteCaptureIndex

# --- PAGE CONFIG ---
st.set_page_config(page_title="Oligarchy Simulator", layout="wide", initial_sidebar_state="expanded")

# --- SESSION STATE SETUP ---
if 'elite_list' not in st.session_state:
    st.session_state['elite_list'] = [
        {'name': "Elon Musk", 'x': 0.5, 'y': -0.5, 'weight': 0.35}
    ]

if 'sim_state' not in st.session_state:
    st.session_state['sim_state'] = 'SETUP' 
if 'sim_data' not in st.session_state:
    st.session_state['sim_data'] = None
if 'current_frame' not in st.session_state:
    st.session_state['current_frame'] = 0

# --- HELPER: POLITICAL COMPASS FIGURE ---
def get_compass_fig(public_pos, policy_pos, elite_list, current_weights=None):
    fig = go.Figure()

    # 1. Background Quadrants
    fig.add_shape(type="rect", x0=0, y0=0, x1=1.5, y1=1.5, 
        fillcolor="rgba(50, 100, 255, 0.1)", layer="below", line_width=0)
    fig.add_shape(type="rect", x0=-1.5, y0=0, x1=0, y1=1.5, 
        fillcolor="rgba(255, 50, 50, 0.1)", layer="below", line_width=0)
    fig.add_shape(type="rect", x0=-1.5, y0=-1.5, x1=0, y1=0, 
        fillcolor="rgba(50, 200, 50, 0.1)", layer="below", line_width=0)
    fig.add_shape(type="rect", x0=0, y0=-1.5, x1=1.5, y1=0, 
        fillcolor="rgba(255, 200, 0, 0.1)", layer="below", line_width=0)

    # 2. Elite Centroid
    if elite_list:
        e_x = [e['x'] for e in elite_list]
        e_y = [e['y'] for e in elite_list]
        w = current_weights if current_weights is not None else [e['weight'] for e in elite_list]
        
        if sum(w) > 0:
            c_x = np.average(e_x, weights=w)
            c_y = np.average(e_y, weights=w)
            fig.add_trace(go.Scatter(
                x=[c_x], y=[c_y], mode='markers', name='Elite Consensus',
                marker=dict(size=22, color='purple', symbol='star', line=dict(width=2, color='white')),
                hoverinfo='name'
            ))

    # 3. Elites
    if elite_list:
        e_names = [e['name'] for e in elite_list]
        e_x = [e['x'] for e in elite_list]
        e_y = [e['y'] for e in elite_list]
        
        if current_weights is not None:
            sizes = [15 + (wt * 20) for wt in current_weights]
            hover_txt = [f"{n}<br>Power: {wt:.2f}" for n, wt in zip(e_names, current_weights)]
        else:
            sizes = [15 + (e['weight'] * 20) for e in elite_list]
            hover_txt = [f"{e['name']}<br>Init Power: {e['weight']:.2f}" for e in elite_list]

        fig.add_trace(go.Scatter(
            x=e_x, y=e_y, mode='markers+text', name='Individual Elites',
            marker=dict(size=sizes, color='black', symbol='diamond', line=dict(width=1, color='white')),
            text=e_names, textposition="top center",
            hovertext=hover_txt, hoverinfo="text"
        ))

    # 4. Public
    fig.add_trace(go.Scatter(
        x=[public_pos[0]], y=[public_pos[1]], mode='markers', name='Public Opinion',
        marker=dict(size=22, color='blue', symbol='circle', line=dict(width=2, color='white'))
    ))

    # 5. Policy
    fig.add_trace(go.Scatter(
        x=[policy_pos[0]], y=[policy_pos[1]], mode='markers', name='Policy Outcome',
        marker=dict(size=20, color='green', symbol='x', line=dict(width=4, color='white'))
    ))

    fig.update_layout(
        xaxis=dict(range=[-1.5, 1.5], title="Economic (Left ↔ Right)", zeroline=True, fixedrange=True, showgrid=False),
        yaxis=dict(range=[-1.5, 1.5], title="Social (Lib ↔ Auth)", zeroline=True, fixedrange=True, showgrid=False),
        height=550, margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white", uirevision='constant'
    )
    return fig

def get_gauge_fig(value, title, color, frame_idx=0):
    # Micro-adjustment to prevent duplicate ID error on static frames
    unique_val = value + (frame_idx * 1e-9)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = unique_val,
        title = {'text': title, 'font': {'size': 20, 'color': 'black'}},
        number = {'font': {'size': 30}},
        gauge = {
            'axis': {'range': [None, 1], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "gray",
            'steps': [{'range': [0, 1], 'color': 'rgba(240, 242, 246, 0.5)'}]
        }
    ))
    fig.update_layout(height=180, margin=dict(l=30, r=30, t=50, b=10)) 
    return fig

def get_result_card(avg_theta, avg_eci):
    """
    Verdict based strictly on Democratic Responsiveness.
    """
    if avg_theta >= 0.70:
        verdict = "HEALTHY DEMOCRACY"
        color = "#28a745" # Green
        desc = "The government effectively translates public preference into policy."
    elif avg_theta >= 0.50:
        verdict = "FLAWED DEMOCRACY"
        color = "#17a2b8" # Teal
        desc = "The public has influence, but elite pressure regularly skews outcomes."
    elif avg_theta >= 0.30:
        verdict = "OLIGARCHIC CAPTURE"
        color = "#fd7e14" # Orange
        desc = "Democratic institutions exist but predominantly serve elite interests."
    else:
        verdict = "TOTAL OLIGARCHY"
        color = "#dc3545" # Red
        desc = "The state apparatus has been completely co-opted by the ruling class."

    return f"""
    <div style="
        border: 3px solid {color}; 
        border-radius: 15px; 
        padding: 20px; 
        text-align: center; 
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;">
        <h2 style="color: {color}; margin: 0; font-size: 2em; letter-spacing: 1px;">{verdict}</h2>
        <p style="color: #666; font-size: 0.9em; text-transform: uppercase; margin-top: 5px;">System Diagnostic Complete</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 15px 0;">
        <div style="display: flex; justify-content: space-around; margin-bottom: 15px;">
            <div>
                <div style="font-size: 2.5em; font-weight: bold; color: #333;">{avg_theta:.2f}</div>
                <div style="font-size: 0.8em; color: #888;">AVG DEMOCRACY SCORE</div>
            </div>
            <div>
                <div style="font-size: 2.5em; font-weight: bold; color: #333;">{avg_eci:.2f}</div>
                <div style="font-size: 0.8em; color: #888;">AVG ELITE CAPTURE</div>
            </div>
        </div>
        <div style="background-color: {color}15; padding: 10px; border-radius: 8px; color: {color}; font-weight: bold;">
            {desc}
        </div>
    </div>
    """


# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("Configurations")
    T = st.slider("Cycles", 50, 200, 100)
    
    # EXPLANATION STRINGS
    help_noise = "Random shocks to public opinion (e.g., wars, pandemics, scandals).\n\nINCREASES WITH: Instability, Polarization.\nDECREASES WITH: Social Cohesion, Stable Media."
    help_theta_base = "The natural level of democracy the system returns to if elite capture is zero.\n\nINCREASES WITH: Strong Constitution, Civic Education.\nDECREASES WITH: Gerrymandering, Voter Suppression."
    help_alpha = "How fast institutions heal from corruption.\n\nINCREASES WITH: Anti-Corruption Laws, Transparency.\nDECREASES WITH: Rulings like Citizens United, Partisan Courts."
    help_lambda = "How quickly elite capture destroys democratic responsiveness.\n\nINCREASES WITH: Dark Money, Lobbying Loopholes.\nDECREASES WITH: Campaign Finance Limits."
    help_eta = "How quickly the public accepts the new status quo (policy) as their own preference.\n\nINCREASES WITH: Propaganda, Media Monopolies.\nDECREASES WITH: Critical Thinking, Independent Journalism."
    help_kappa = "How much more power elites get when they 'win'.\n\nINCREASES WITH: Wealth Inequality, Unregulated Markets.\nDECREASES WITH: Progressive Taxes, Antitrust Laws."

    noise_scale = st.slider("Noise", 0.0, 0.2, 0.1, step=0.01, help=help_noise)
    
    st.divider()
    st.subheader("System Parameters")
    theta_0 = st.slider("Initial Democracy Score", 0.0, 1.0, 0.7, help="Starting level of democratic responsiveness.")
    theta_star = st.slider("Baseline Democracy", 0.0, 1.0, 0.8, help=help_theta_base)
    
    st.divider()
    st.subheader("Rates")
    alpha = st.slider("Recovery Rate", 0.0, 0.5, 0.1, step=0.01, help=help_alpha)
    lambd = st.slider("Erosion Rate", 0.0, 0.5, 0.05, step=0.01, help=help_lambda)
    
    st.divider()
    eta = st.slider("Public Learning Rate", 0.0, 1.0, 0.05, help=help_eta)
    kappa = st.slider("Elite Power Sensitivity", 0.0, 5.0, 1.0, help=help_kappa)


# --- MAIN APP LOGIC ---
st.title("Oligarchy Simulator")

# SINGLE CONTAINER FOR PAGE CONTENT
main_display = st.empty()

# -----------------
# 1. SETUP STATE
# -----------------
if st.session_state['sim_state'] == 'SETUP':
    with main_display.container():
        col_left, col_right = st.columns([1, 1.5], gap="large")
        
        with col_left:
            st.subheader("1. Public Opinion")
            p_col1, p_col2 = st.columns(2)
            m0_x = p_col1.number_input("Econ (X)", -1.5, 1.5, 0.0, step=0.1)
            m0_y = p_col2.number_input("Social (Y)", -1.5, 1.5, 0.0, step=0.1)
            
            st.markdown("---")
            st.subheader("2. Add Elites")
            with st.form("add_elite_form", clear_on_submit=True):
                e_name = st.text_input("Name", "Wall St")
                ec1, ec2, ec3 = st.columns(3)
                e_x = ec1.number_input("X", -1.5, 1.5, 0.5)
                e_y = ec2.number_input("Y", -1.5, 1.5, 0.5)
                e_w = ec3.number_input("Power", 0.1, 5.0, 0.2)
                if st.form_submit_button("Add Elite"):
                    st.session_state['elite_list'].append({
                        'name': e_name, 'x': e_x, 'y': e_y, 'weight': e_w
                    })
                    st.rerun()

            if st.session_state['elite_list']:
                st.caption("Current Elites:")
                for i, e in enumerate(st.session_state['elite_list']):
                    c1, c2 = st.columns([3, 1])
                    c1.text(f"{e['name']}: ({e['x']},{e['y']}) w={e['weight']}")
                    if c2.button("❌", key=f"del_{i}"):
                        st.session_state['elite_list'].pop(i)
                        st.rerun()

            st.markdown("---")
            if st.button("START SIMULATION", type="primary", use_container_width=True):
                M_0 = np.array([m0_x, m0_y])
                results = run_simulation(
                    T, M_0, theta_0, st.session_state['elite_list'], 
                    eta, kappa, lambd, noise_scale, alpha, theta_star
                )
                st.session_state['sim_data'] = results
                st.session_state['sim_state'] = 'PLAYING'
                st.session_state['current_frame'] = 0
                st.rerun()

        with col_right:
            M_start = [m0_x, m0_y]
            fig = get_compass_fig(M_start, M_start, st.session_state['elite_list'])
            st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# 2. RUNNING / FINISHED STATE
# ----------------------------
else:
    results = st.session_state['sim_data']
    
    with main_display.container():
        # Compact Dashboard
        col_metrics, col_chart = st.columns([1, 2])
        
        with col_metrics:
            # Placeholders
            result_slot = st.empty()
            cycle_slot = st.empty()
            
            theta_slot = st.empty()
            theta_avg_slot = st.empty()
            
            eci_slot = st.empty()
            eci_avg_slot = st.empty()
            
            st.markdown("---")
            c_play, c_reset = st.columns(2)
            btn_play = c_play.button("▶️ Run")
            btn_reset = c_reset.button("↺ Reset")

        with col_chart:
            # Chart Legend / Help Tooltips
            # We use st.caption to provide the requested legend help
            l1, l2, l3, l4 = st.columns(4)
            l1.caption("🔵 **Public**", help="The median voter's preference.")
            l2.caption("✖️ **Policy**", help="The actual law/outcome implemented.")
            l3.caption("♦️ **Elites**", help="Powerful actors (Corps, Unions) vying for influence.")
            l4.caption("⭐️ **Consensus**", help="The weighted average 'Elite Agenda'.")
            
            chart_slot = st.empty()

        # Handle Reset
        if btn_reset:
            st.session_state['sim_state'] = 'SETUP'
            st.session_state['current_frame'] = 0
            st.rerun()

        # Handle Animation
        if st.session_state['sim_state'] == 'PLAYING' or btn_play:
            st.session_state['sim_state'] = 'PLAYING'
            data = st.session_state['sim_data']
            
            for i in range(st.session_state['current_frame'], len(data)):
                frame = data[i]
                
                # Metrics
                eci = eliteCaptureIndex(frame.M, frame.E, frame.O)
                cycle_slot.metric("Cycle", f"{frame.t} / {len(data)}")
                
                theta_slot.plotly_chart(get_gauge_fig(frame.theta, "Democracy Score", "blue", i), use_container_width=True, config={'displayModeBar': False})
                eci_slot.plotly_chart(get_gauge_fig(eci, "Elite Capture", "red", i), use_container_width=True, config={'displayModeBar': False})
                
                if i > 5:
                    sub = data[5:i+1]
                    avg_t = np.mean([x.theta for x in sub])
                    avg_e = np.mean([eliteCaptureIndex(x.M, x.E, x.O) for x in sub])
                    theta_avg_slot.caption(f"Avg: {avg_t:.2f}")
                    eci_avg_slot.caption(f"Avg: {avg_e:.2f}")

                chart_slot.plotly_chart(get_compass_fig(frame.M, frame.O, st.session_state['elite_list'], frame.w), use_container_width=True, config={'displayModeBar': False})

                time.sleep(0.08)
                st.session_state['current_frame'] = i
            
            st.session_state['sim_state'] = 'FINISHED'
            st.rerun()

        # Finished View
        if st.session_state['sim_state'] == 'FINISHED':
            data = st.session_state['sim_data']
            last = data[-1]
            valid = data[5:] if len(data) > 5 else data
            
            final_t = np.mean([x.theta for x in valid])
            final_e = np.mean([eliteCaptureIndex(x.M, x.E, x.O) for x in valid])
            
            result_slot.markdown(get_result_card(final_t, final_e), unsafe_allow_html=True)
            
            cycle_slot.metric("Cycle", "Finished")
            theta_slot.plotly_chart(get_gauge_fig(last.theta, "Democracy Score", "blue", 999), use_container_width=True, config={'displayModeBar': False})
            eci_slot.plotly_chart(get_gauge_fig(eliteCaptureIndex(last.M, last.E, last.O), "Elite Capture", "red", 999), use_container_width=True, config={'displayModeBar': False})
            theta_avg_slot.caption(f"Final Avg: {final_t:.2f}")
            eci_avg_slot.caption(f"Final Avg: {final_e:.2f}")
            
            chart_slot.plotly_chart(get_compass_fig(last.M, last.O, st.session_state['elite_list'], last.w), use_container_width=True, config={'displayModeBar': False})