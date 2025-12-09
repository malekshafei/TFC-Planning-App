import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import numpy as np
from datetime import datetime, date
import uuid
from PIL import Image, ImageOps
import matplotlib.font_manager as fm


import time 
import os
import io


import matplotlib.pyplot as plt

regular_font_path = 'Montserrat-Regular.ttf'
bold_font_path = 'Montserrat-Bold.ttf'

import matplotlib.font_manager as font_manager
from matplotlib import font_manager, rcParams

font_manager.fontManager.addfont(regular_font_path)
font_manager.fontManager.addfont(bold_font_path)
rcParams['font.family'] = 'Montserrat'
mode1 = 'Basic'

# Page configuration
st.set_page_config(
    page_title="TFC App",
    page_icon="⚽",
    layout="wide"
)


team_rankings = {
    'FCM': 1,
    'CDM': 2,
    'FCM U19': 3,
    'FCM Next Gen': 4,
    'FCM U17': 5,
    'FCM U15': 6,
    'FCE': 7
}

df = pd.read_excel("TFC Players Working.xlsx")
# Sort by team priority, then by Team Rank within each team
df['Team Priority'] = df['Team'].map(team_rankings)
df = df.sort_values(['Position', 'Team Priority', 'Team Rank'])

# Create TFC Rank within each position group
df['TFC Rank'] = df.groupby('Position').cumcount() + 1

# Clean up temporary column
df = df.drop('Team Priority', axis=1)

df.sort_values(by=['TFC Rank', 'Position'] )

df = df.fillna("-")

# Main app 
def main():
    st.title("TFC Planning App")
    sheet_url = "https://docs.google.com/spreadsheets/d/17PXkZUNFAgFYnW2m0NshoN23GP681tYXNB1S1kM109Q/edit?gid=0#gid=0"
    new_sheet_url = "https://docs.google.com/spreadsheets/d/15xMZWoD9dy-eMgnp5cbHXquHuyXHylBbUc2fzHS056E/edit?gid=0#gid=0"
    st.session_state["sheet_url"] = sheet_url
    st.session_state["new_sheet_url"] = new_sheet_url

    

     

    # Sidebar for configuration
    with st.sidebar:
        st.header("Login")
        # sheet_url = st.text_input(
        #     "Google Sheet URL",
        #     value=st.session_state.get("sheet_url", ""),
        #     help="Paste your Google Sheet URL here"
        # )
        
        # if sheet_url:
        #     st.session_state["sheet_url"] = sheet_url
        
        # Scout login
        #st.markdown("---")
        #st.subheader("Login")
        scout_name = st.text_input("Name", value=st.session_state.get("scout_name", ""))
        if scout_name:
            st.session_state["scout_name"] = scout_name
            st.success(f"Logged in as: {scout_name}")
        
        st.markdown("---")

        st.write("Load Previous Versions??")

    tab1, tab2, tab3, = st.tabs(["📊 TFC Overview", "🏟️ Team Overview", "👤 Player View"])
    
    with tab1:
        st.dataframe(df, hide_index=True)
    with tab2:
        team_overview(df)
    with tab3:
        player_view(df)


def team_overview(df):

    from PIL import Image, ImageDraw, ImageFont
    import io
    
    
    selected_team = st.selectbox("Select Team", ['FCM', 'CDM', 'FCM U19', 'FCM Next Gen', 'FCM U17', 'FCM U15', 'FCE'])
    team_df = df[df['Team'] == selected_team]

    selected_year = st.selectbox("Select Year", ['Current', '2026/27', '2027/28', '2028/29'])
    if selected_year == 'Current': pass
    elif selected_year == '2026/27': 
        team_df = df[df['26/27'] == selected_team]
    elif selected_year == '2027/28': 
        team_df = df[df['27/28'] == selected_team]
    elif selected_year == '2028/29': 
        team_df = df[df['28/29'] == selected_team]


    


    if len(team_df) == 0: 
        st.warning(f"0 Players on {selected_team} in {selected_year}")

    else:
        
        position_order = {
            1: 1,
            2: 5,
            3: 6,
            4: 3, 
            '5L': 2,
            '5R': 4,
            6: 7, 
            8: 8,
            10: 9,
            7: 10,
            11: 11,
            9: 12
        }
        team_df['Position Order'] = team_df['Position'].map(position_order).fillna(13)
        
        #shadow_team_df = shadow_team_df.sort_values(by=['Position Order', 'CR', 'PR'], ascending = [True, False, False])
        
        
        st.subheader(f"{selected_team} - Overview")
        
        # Position coordinates on the pitch (x, y) - scaled for 2400x1350
        position_coords = {
            1: (100, 670),      # GK
            2: (635, 885),     # LB
            3: (635, 145),      # RB
            #4: (470, 580),      # CB (center)
            5: (500, 520),   # LCB
            #'5R': (470, 930),   # RCB
            6: (780, 320),      # CDM 
            8: (1025, 745),     # CM
            10: (1200, 320),    # CAM
            7: (1480, 880),     # RW
            11: (1480, 145),   # LW
            9: (1535, 515)      # ST
        }
        
        # Load background image
        img = Image.open('FCM Shadow Team Image.png')#.resize((2400, 1350))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (img.width, 105)], fill='#0c1116')
        
        # Try to load a custom font, fallback to default
        # try:
        #     font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 40)
        #     small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 30)
        # except:
        #     font = ImageFont.load_default()
        #     small_font = ImageFont.load_default()

        font = ImageFont.truetype("Montserrat-Bold.ttf", 27)
        
        # Group players by position and draw them
        for _, player_row in team_df.iterrows():
            position = player_row['Position']
        
        for position in team_df['Position'].unique():
            x, y = position_coords[position]
            i = 1
            for _, player_row in team_df[team_df['Position'] == position].iterrows():
                
                player_color = player_row['Category']
                
                # Create player text: Name (Birthyear)
                player_name = player_row['Player']
                birth_year = player_row['DOB'][-2:] if isinstance(player_row['DOB'], str) and len(str(player_row['DOB'])) >= 4 else str(player_row['DOB'])
                
                if len(player_name) > 12:
                    name_parts = player_name.split()
                    if len(name_parts) >= 2:
                        player_name = name_parts[0][0] + '. ' + name_parts[-1]
                player_text = f"{i}. {player_name} ({birth_year})"
                
                
                draw.text((x, y), player_text, 
                         fill=player_color, font=font, ha = 'left')
                

                # Calculate the width of the player text to position indicators
                bbox = draw.textbbox((x, y), player_text, font=font, anchor='lm')
                text_end_x = bbox[2]  # Right edge of the text

                # Build indicator text
                indicators = []
                # if player_row.get('SP Taker?') == 'Yes':
                #     indicators.append('SP')
                # if player_row.get('SP Threat?') == 'Yes':
                #     indicators.append('SPt')

                # Check contract expiry
                contract_expiry = str(player_row.get('Contract', ''))
                if len(contract_expiry) >= 2 and contract_expiry[-2:] in ['25', '26']:
                    indicators.append('OOC') 

                # Draw indicators in yellow to the right
                if indicators:
                    indicator_text = ' ' + ' '.join(indicators)
                    draw.text((text_end_x + 2, y), indicator_text, fill='green', font=font, ha = 'left')
                
                y += 35
                i += 1

        #font2 = ImageFont.truetype("Montserrat-Bold.ttf", 50)
        #draw.text((85,40),f"{selected_team} - {selected_year}", fill='black', font=font2, ha = 'left' )
        # Load and paste team logo
        team_logos = {
             'FCM': 'TFC Logos/FCM.png',
                'CDM': 'TFC Logos/CD Mafra.png',
                'FCM U19': 'TFC Logos/FCM U19.png',
                'FCM Next Gen': 'TFC Logos/FCM Next Gen.png',
                'FCM U17': 'TFC Logos/FCM U17.png',
                'FCM U15': 'TFC Logos/FCM U15.png',
                'FCE': 'TFC Logos/FC Ebedei.png',
        }

        # Add logo on the left
        if selected_team in team_logos:
            try:
                logo = Image.open(team_logos[selected_team])

                logo_width = logo.width
                
                #logo = logo.crop((0, 0, 700, logo.height))
                # Resize logo (adjust size as needed)
                #logo = logo.resize((150, 107))

                logo = logo.resize((300, 100))

                # Paste logo with transparency if available
                if logo.mode == 'RGBA':
                    img.paste(logo, (85, 5), logo)
                else:
                    img.paste(logo, (85, 20))
            except:
                pass

        # Add selected year text on the right
        # font2 = ImageFont.truetype("Montserrat-Bold.ttf", 50)
        # draw.text((250,30), f"{selected_team} - {selected_year}", fill='black', font=font2)
        font2 = ImageFont.truetype("Montserrat-Regular.ttf", 40)
        draw.text((1700,30), f"{selected_year}", fill='white', font=font2, ha='right')
        # Display image
        st.image(img, caption=f"{selected_team} - {selected_year} -  Shadow Team", use_container_width=True)
        
        # Download button
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        byte_im = buf.getvalue()
        
        st.download_button(
            label="Download Formation Image",
            data=byte_im,
            file_name=f"{selected_team}_{selected_year}_shadow_team.png",
            mime="image/png"
        )

    st.dataframe(team_df, hide_index=True)


def player_view(df):
    df['Clean Name'] = df['Player'] + ' (' + df['Team'] + ' - #' + df['Position'].astype(str) + ' - ' + df['Age'].astype(str) + ')'

    selected_player = st.selectbox("Select Player", df['Clean Name'].unique())

    if selected_player != None:
        
        player_row = df[df['Clean Name'] == selected_player].iloc[0]
        id = player_row['TFC ID']
        player_name = player_row['Player']
        player_position = player_row['Position']
        team_name = player_row['Team']
        player_dob = player_row['DOB'] 

        st.header(player_name)

        col1, col2, col3, col4 = st.columns([0.35,0.35,0.5, 0.2 ])
        with col1:
            st.image("KPE.png", width=700)
        with col2:
            st.metric("Age", player_row['Age'])
            st.metric("Homegrown (Club)", player_row['Homegrown (Club-Trained)'])
            st.metric("Homegrown (Federation)", player_row['Homegrown (Association-Trained)'])
        
        with col3: 
            st.metric("Height", f"{player_row['Height']}cm")
            #st.metric("DOB", player_row['DOB'])
            st.metric("Contract Expires", player_row['Contract'])
            if player_row['On Loan?'] == 'Yes': st.metric("On Loan", player_row['Loan Team'])
            
        with col4:
            st.metric("Position", player_row['Position'])
            st.metric(f"{team_name} Rank", f"#{player_row['Team Rank']}")
            st.metric(f"TFC Rank", f"#{player_row['TFC Rank']}")
        
        col1, col2, col3, col4 = st.columns(4)
        pathway_options = ['FCM', 'CDM', 'FCM U19', 'FCM U17', 'FCM U15', 'FCM Next Gen', 'FCE', 'Loan', 'Out']
        with col1: st.metric("2025/26", player_row['Team'])
        

        with col2:
            st.markdown("2026/27")
            selected_pathway = st.selectbox(" ", pathway_options,
                                            index=pathway_options.index(player_row['26/27']) if player_row['26/27'] in pathway_options else 0,
                                            label_visibility="collapsed", key='26/27')
            
        with col3:
            st.markdown("2027/28")
            selected_pathway = st.selectbox(" ", pathway_options,
                                            index=pathway_options.index(player_row['27/28']) if player_row['27/28'] in pathway_options else 0,
                                            label_visibility="collapsed", key='27/28')
            
        with col4:
            st.markdown("2028/29")
            selected_pathway = st.selectbox(" ", pathway_options,
                                            index=pathway_options.index(player_row['28/29']) if player_row['28/29'] in pathway_options else 0,
                                            label_visibility="collapsed", key='28/29')
            

        st.write("")
        st.write("")

        col1, col2 = st.columns([0.65, 0.35])

        with col1: 
            import pandas as pd

            history = pd.read_excel("TFC Career History.xlsx")
            history = history[history['TFC ID'] == id].sort_values(by='Index')

            st.header("Career History")
            st.dataframe(history[['Season', 'Team', 'League', 'Games', 'Minutes']], hide_index=True)
            st.write("add 25/26 data from merge")
            st.write("")


        with col2:
            # pos_df = df[df['Position'] == player_position].sort_values(by = 'TFC Rank')
            # i = 1
            # for _, row in pos_df.iterrows():
            #     player_text = f"{i}. {row['Shortened Name']} ({row['Team']} - {row['Age']})"
            #     if row['TFC ID'] == id: st.markdown(f"**{player_text}**")
            #     else: st.text(player_text)
            #     i += 1

            import plotly.graph_objects as go
            from PIL import Image
            import requests
            from io import BytesIO

            st.header("Positional Competition")

            pos_df = df[df['Position'] == player_position].sort_values(by='TFC Rank')

            # Group by team
            teams = pos_df['Team'].unique()

            # Create figure
            fig = go.Figure()

            # Track vertical position
            y_position = 0
            y_spacing = 0.8  # Space between players
            logo_spacing = 1.5  # Extra space for logo

            # Dictionary to store team logo paths (you'll need to set these up)
            team_logos = {
                'FCM': 'TFC Logos/FCM.png',
                'CDM': 'TFC Logos/CD Mafra.png',
                'FCM U19': 'TFC Logos/FCM U19.png',
                'FCM Next Gen': 'TFC Logos/FCM Next Gen.png',
                'FCM U17': 'TFC Logos/FCM U17.png',
                'FCM U15': 'TFC Logos/FCM U15.png',
                'FCE':'TFC Logos/FC Ebedei.png',
                # Add more teams as needed 
            }

            rank = 1
            for team in teams:
                team_players = pos_df[pos_df['Team'] == team]
                y_position -= logo_spacing

                
                # Add team logo as image
                if team in team_logos:
                    try:
                        # Try to load the logo
                        img = Image.open(team_logos[team])
                        
                        # Add logo image
                        fig.add_layout_image(
                            dict(
                                source=img,
                                xref="x",
                                yref="y",
                                x=0.5,
                                y=y_position + 0.3,
                                sizex=1.5,
                                sizey=1.5,
                                xanchor="center",
                                yanchor="middle",
                                layer="above"
                            )
                        )
                    except:
                        # If logo not found, just show team name
                        fig.add_annotation(
                            x=0.5,
                            y=y_position + 0.3,
                            text=f"<b>{team}</b>",
                            showarrow=False,
                            font=dict(size=16, color='white'),
                            xanchor='center'
                        )
                else:
                    # No logo, show team name
                    fig.add_annotation(
                        x=0.5,
                        y=y_position + 0.3,
                        text=f"<b>{team}</b>",
                        showarrow=False,
                        font=dict(size=16, color='white'),
                        xanchor='center'
                    )
                
                y_position -= logo_spacing
                
                # Add players for this team
                for _, row in team_players.iterrows():
                    player_name = row['Shortened Name']
                    age = row['Age']
                    
                    # Check if this is the selected player
                    is_selected = row['TFC ID'] == id
                    
                    # Rank number
                    fig.add_annotation(
                        x=0.1,
                        y=y_position,
                        text=f"<b>{rank}.</b>",
                        showarrow=False,
                        font=dict(
                            size=14,
                            color='red' if is_selected else 'white',
                            family='monospace'
                        ),
                        xanchor='left'
                    )
                    
                    # Player name and age
                    fig.add_annotation(
                        x=0.3,
                        y=y_position,
                        text=f"<b>{player_name}</b> ({age})" if is_selected else f"{player_name} ({age})",
                        showarrow=False,
                        font=dict(
                            size=14,
                            color='red' if is_selected else 'white'
                        ),
                        xanchor='left'
                    )
                    
                    # Optional: Add highlight box for selected player
                    if is_selected:
                        fig.add_shape(
                            type="rect",
                            x0=0.05,
                            y0=y_position - 0.3,
                            x1=0.95,
                            y1=y_position + 0.3,
                            line=dict(color='red', width=2),
                            fillcolor='rgba(0, 212, 255, 0.1)'
                        )
                    
                    y_position -= y_spacing
                    rank += 1
                
                # Add extra space between teams
                y_position -= 0.5

            # Update layout
            fig.update_layout(
                height=max(600, len(pos_df) * 50 + len(teams) * 80),  # Dynamic height based on content
                xaxis=dict(
                    range=[0, 1],
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False
                ),
                yaxis=dict(
                    range=[y_position - 1, 1],
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False
                ),
                plot_bgcolor='#0c1116',
                paper_bgcolor='#0c1116',
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
              

        with col1:
            ##### RADAR #############################
            st.header("Player Data")

            data = pd.read_parquet("TFC Test Data.parquet")
            data = data.fillna(0)

            data['Title'] = data.apply(
                lambda row: f"{row['Player']} ({row['Team within selected timeframe']} - {row['league_name']} - {row['Season']}) - {row['Minutes played']} mins",
                axis=1
            )

            if player_position == 1: metrics = ['GK_Shot Stopping', 'GK_Short Distribution', 'GK_Long Distribution']
            elif player_position == 4: metrics = ['Tackle Accuracy', 'Defensive Output', 'Heading', 'Ball Retention','Carrying', 'Progression',  ]
            elif player_position == 3: metrics = ['Tackle Accuracy', 'Defensive Output', 'Heading', 'Ball Retention', 'Carrying', 'Progression', 'Chance Creation']
            elif player_position in [6,8]: metrics = ['Tackle Accuracy', 'Defensive Output', 'Ball Retention', 'Carrying', 'Progression', 'Chance Creation', 'Heading', 'Receiving']
            elif player_position in [7,10,11]: metrics = ['Defensive Output', 'Dribbling', 'Progression', 'Chance Creation', 'Poaching', 'Finishing']
            elif player_position == 9: metrics = ['Defensive Output', 'Ball Retention', 'Dribbling', 'Chance Creation', 'Poaching', 'Finishing', 'Heading']
            

            
       
            player_data = data[data['TFC ID'] == id].sort_values(by = 'Season Order', ascending=False)

            selected_row_name = st.selectbox("Select Season", player_data['Title'].unique())

            selected_row = data[data['Title'] == selected_row_name]

        

            compare = st.checkbox("Compare with another TFC Player?")
            
            if compare:

                selected_player2 = st.selectbox("Select Player", df['Player'].unique(), key = 'player_2')
                player_row2 = df[df['Player'] == selected_player2].iloc[0]
                pid2 = player_row2['TFC ID']
                player_data2 = data[data['TFC ID'] == pid2].sort_values(by = 'Season Order', ascending=False)
                selected_row_name2 = st.selectbox("Select Season", player_data2['Title'].unique(), key = 'season_2')
                selected_row2 = data[data['Title'] == selected_row_name2]

                print(selected_row_name2)
                


        
            data1 = []
            data2 = []
            for metric in metrics: 
                data1.append(selected_row.iloc[0][metric])
                if compare: data2.append(selected_row2.iloc[0][metric])
            
           

            
            metric_names = metrics
            
            
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            
            data1_plot = data1 + data1[:1]
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            angles_plot = angles + angles[:1]

            if compare:
                data2_plot = data2 + data2[:1]


            # Create figure with polar plot
            fig, ax = plt.subplots(figsize=(16, 9), subplot_kw=dict(polar=True, facecolor="#0c1116"))
            fig.patch.set_facecolor('#0c1116')
            ax.set_facecolor('#0c1116')
            ax.spines['polar'].set_visible(False)

            #ax.set_title(f'{selected_row_name}', fontsize=20, color='white', weight='bold', ha = 'center',pad=30)
            #fig.suptitle(f'{selected_row_name}', fontsize=20, color='white', ha = 'center', weight='bold', y=0.98)
            
            if compare:            
                fig.text(0.5, 1.0, f'{selected_row_name}',
                    fontsize=20, color='red', weight='bold', 
                    ha='center', va='top')
                fig.text(0.5, 0.95, f'vs. {selected_row_name2}',
                    fontsize=20, color='white', weight='bold', 
                    ha='center', va='top')
                
            else:
                fig.text(0.5, 0.95, f'{selected_row_name}',
                    fontsize=20, color='white', weight='bold', 
                    ha='center', va='top')

            
            



            # KEY: Set origin offset like your working code
            ax.set_rorigin(-2)

            # Draw grid circles
            ax.plot(angles_plot, [100] * len(angles_plot), color='white', linewidth=2.25, linestyle='-')
            ax.plot(angles_plot, [75] * len(angles_plot), color='white', linewidth=0.7, linestyle='-')
            ax.plot(angles_plot, [50] * len(angles_plot), color='white', linewidth=0.7, linestyle='-')
            ax.plot(angles_plot, [25] * len(angles_plot), color='white', linewidth=0.7, linestyle='-')

            # Plot data
            if compare == False:
                ax.plot(angles_plot, data1_plot, color='red', linewidth=2.5, linestyle='-', marker='o', markersize=5)
                ax.fill(angles_plot, data1_plot, color='red', alpha=0.95)
                
            elif compare == True:
                ax.plot(angles_plot, data1_plot, color='red', linewidth=2.5, linestyle='-', marker='o', markersize=5)
                ax.fill(angles_plot, data1_plot, color='red', alpha=0.7)
                
                ax.plot(angles_plot, data2_plot, color='white', linewidth=2.5, linestyle='-', marker='o', markersize=5)
                ax.fill(angles_plot, data2_plot, color='white', alpha=0.55)

            # Add labels directly to polar plot (like your working code)
            label_radius = 105

            for i, angle in enumerate(angles):
                # Calculate rotation for text
                rotation = np.degrees(angle)
                if rotation > 90 and rotation < 270:
                    rotation -= 180
                    ha = 'right'
                else:
                    ha = 'left'
                
                # Get metric name
                metric_name = metric_names[i]
                
                # Handle special angles (top and bottom)
                if abs(angle - np.pi/2) < 0.01: ha = 'center'
                elif abs(angle - 3*np.pi/2) < 0.01:  ha = 'center'
                    
                ax.text(angle, label_radius, metric_name,
                            ha=ha, va='center', fontsize=17, color='white')

            # Configure axes
            ax.set_xticks(angles)
            ax.set_xticklabels([''] * len(metrics))
            ax.set_yticks([])
            ax.set_ylim(0, 100)
            ax.plot(0, 0, 'ko', markersize=2, color='#0c1116')
            fig.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)

            # Save directly to buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', facecolor='#0c1116')
            buf.seek(0)

            plt.close(fig)



            # plt.savefig("PIctestjuly3.png")

            #st.pyplot(plt)

                
            st.image(buf, use_container_width=True)




            st.write("")
            st.header("Progression")

            history = pd.read_excel("TFC Career History.xlsx")
             #history has rows for each player ['TFC ID', 'Player', 'Season', 'Team', 'League', 'Games', 'Minutes]
            id2 = 92
            id3 = None
            id4 = None

           
            season_mid_dates = {
                '17/18': "01-01-2018",
                '18/19': "01-01-2019",
                '19/20': "01-01-2020",
                '20/21': "01-01-2021",
                '21/22': "01-01-2022",
                '22/23': "01-01-2023",
                '23/24': "01-01-2024",
                '24/25': "01-01-2025",
                '25/26': "01-01-2026",
                '2020': "01-06-2020",
                '2021': "01-06-2021",
                '2022': "01-06-2022",
                '2023': "01-06-2023",
                '2024': "01-06-2024",
                '2025': "01-06-2025",
            }


            import plotly.graph_objects as go
            import pandas as pd

            # Add age calculation
            history = pd.merge(history, df[['TFC ID', 'DOB']], on='TFC ID', how='left')

            # Convert DOB to datetime if not already
            history['DOB'] = pd.to_datetime(history['DOB'])

            # Map seasons to midpoint dates and calculate age
            history['Season_Midpoint'] = history['Season'].map(season_mid_dates)
            history['Season_Midpoint'] = pd.to_datetime(history['Season_Midpoint'], format='%d-%m-%Y')

            # Calculate age at season midpoint
            history['Age'] = (history['Season_Midpoint'] - history['DOB']).dt.days / 365.25

            # List of player IDs to compare
            selected_ids = [id for id in [id, id2, id3, id4] if id is not None]

            # Define player colors (each player gets their own color)
            player_colors = {
                0: '#00d4ff',  # Bright cyan for primary player
                1: '#ff6b6b',  # Red
                2: '#4ecdc4',  # Teal
                3: '#ffe66d',  # Yellow
            }

            # Create figure
            fig = go.Figure()

            # Track player names and colors for title
            player_title_info = []

            # Process each player
            for player_idx, player_id in enumerate(selected_ids):
                player_history = history[history['TFC ID'] == player_id].sort_values(by='Index').copy()
                
                if len(player_history) == 0:
                    continue
                
                # Calculate cumulative minutes
                player_history['Cumulative_Minutes'] = player_history['Minutes'].cumsum()
                
                # Get player name and color
                player_name = player_history['Player'].iloc[0]
                player_color = player_colors[player_idx]
                player_title_info.append((player_name, player_color))
                
                # Line width - primary player is thickest
                line_width = 5 if player_idx == 0 else 3
                
                # Track teams seen for this player
                teams_seen = set()
                
                # Plot line segments
                for i in range(len(player_history) - 1):
                    current_row = player_history.iloc[i]
                    next_row = player_history.iloc[i + 1]
                    
                    # Line segment - all solid lines
                    fig.add_trace(
                        go.Scatter(
                            x=[current_row['Age'], next_row['Age']],
                            y=[current_row['Cumulative_Minutes'], next_row['Cumulative_Minutes']],
                            mode='lines',
                            line=dict(
                                color=player_color,
                                width=line_width
                            ),
                            name=player_name,
                            legendgroup=player_name,
                            showlegend=False,
                            hoverinfo='skip'
                        )
                    )
                
                # Add one legend entry per player
                if len(player_history) > 0:
                    first_row = player_history.iloc[0]
                    fig.add_trace(
                        go.Scatter(
                            x=[None],
                            y=[None],
                            mode='lines+markers',
                            line=dict(color=player_color, width=line_width),
                            marker=dict(color=player_color, size=10),
                            name=player_name,
                            legendgroup=player_name,
                            showlegend=True
                        )
                    )
                
                # Add markers for each season with hover info
                for idx, row in player_history.iterrows():
                    team = row['Team']
                    
                    # Determine marker symbol
                    if team == 'FCM' and team not in teams_seen:
                        marker_symbol = 'star'
                    else:
                        marker_symbol = 'circle'
                    
                    # Check if this is a new team for this player
                    is_new_team = team not in teams_seen
                    teams_seen.add(team)
                    
                    fig.add_trace(
                        go.Scatter(
                            x=[row['Age']],
                            y=[row['Cumulative_Minutes']],
                            mode='markers',
                            marker=dict(
                                color=player_color,
                                size=14 if player_idx == 0 else 10,
                                symbol=marker_symbol,
                                line=dict(color='white', width=2)
                            ),
                            name=player_name,
                            legendgroup=player_name,
                            showlegend=False,
                            hovertemplate=f"<b>{player_name}</b><br>" +
                                        f"<b>Team:</b> {team}<br>" +
                                        f"<b>Season:</b> {row['Season']}<br>" +
                                        f"<b>League:</b> {row['League']}<br>" +
                                        f"<b>Age:</b> {row['Age']:.1f}<br>" +
                                        f"<b>Games:</b> {row['Games']}<br>" +
                                        f"<b>Minutes:</b> {row['Minutes']:,.0f}<br>" +
                                        f"<b>Cumulative:</b> {row['Cumulative_Minutes']:,.0f}<br>" +
                                        '<extra></extra>'
                        )
                    )
                    
                    # Add annotation for new team
                    if is_new_team:
                        fig.add_annotation(
                            x=row['Age'],
                            y=row['Cumulative_Minutes'],
                            text=f"{team}<br>Age {row['Age']:.1f}<br>{row['Season']}",
                            showarrow=True,
                            arrowhead=2,
                            arrowsize=1,
                            arrowwidth=2,
                            arrowcolor=player_color,
                            ax=0,
                            ay=-40,
                            font=dict(
                                size=9,
                                color=player_color
                            ),
                            bgcolor='rgba(12, 17, 22, 0.8)',
                            bordercolor=player_color,
                            borderwidth=1,
                            borderpad=4
                        )

            # Create colored title
            title_html = "Career Progression: "
            for i, (name, color) in enumerate(player_title_info):
                if i > 0:
                    title_html += " vs "
                title_html += f"<span style='color:{color}'>{name}</span>"

            # Update layout
            fig.update_layout(
                title=dict(
                    text=title_html,
                    font=dict(size=20),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title=dict(
                        text='Age',
                        font=dict(color='white')
                    ),
                    showgrid=True,
                    gridcolor='#1a2332',
                    zeroline=False,
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    title=dict(
                        text='Cumulative Minutes',
                        font=dict(color='white')
                    ),
                    showgrid=True,
                    gridcolor='#1a2332',
                    zeroline=False,
                    tickfont=dict(color='white')
                ),
                hovermode='closest',
                height=700,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02,
                    font=dict(size=10, color='white'),
                    bgcolor='rgba(12, 17, 22, 0.8)'
                ),
                plot_bgcolor='#0c1116',
                paper_bgcolor='#0c1116'
            )

            # Display in Streamlit
            st.plotly_chart(fig, use_container_width=True)










        st.write("add Radar. Make file for player-id / wyscout")
        
       

        #Show positional competitors

        #2025 2026 2027 etc

        #Similar to in SL and DK and former FCM players

        ### Academy: Minutes progression over career - comps to Aral, Mikel, etc
        #predict success?









if __name__ == "__main__":
    main()


