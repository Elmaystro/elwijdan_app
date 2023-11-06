import streamlit as st
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pandas.tseries.offsets import DateOffset

st.header("Téléchargez la liste des ventes")
sales_file = st.file_uploader("Téléchargez un fichier Excel pour la liste des commandes", type=["xls", "xlsx"])
s = st.slider("Les taille de la saison", 1, 12, 12)

# Add a button to show or hide the Liste des Ventes data frame
show_data = st.checkbox("Afficher la Liste des Ventes")
calculate_button = st.button("Calculate")
if sales_file is not None:
    sales_df = pd.read_excel(sales_file, engine="openpyxl")

    if show_data:  # Display the data frame if the button is checked
        st.subheader("Liste des Ventes")
        show_dataframe = sales_df.copy()
        show_dataframe['Mois'] = show_dataframe['Mois'].dt.strftime('%B %Y')
        st.dataframe(show_dataframe)

# Fit a SARIMA model
if calculate_button and sales_file is not None:
    sales = sales_df.copy()
    sales['Mois'] = pd.to_datetime(sales['Mois'])
    sales.set_index('Mois', inplace=True)
    sales['Ventes'] = sales['Ventes'].astype(float)  # Ensure the 'Ventes' column has a specific data type

    order = (0, 1, 0)  # Order parameter (p, d, q)
    seasonal_order = (1, 0, 1, s)  # Seasonal order parameter (P, D, Q, m)

    # Fit a SARIMA model
    sarima_model = sm.tsa.SARIMAX(sales['Ventes'], order=order, seasonal_order=seasonal_order)
    sarima_results = sarima_model.fit()

    # Predict future sales using the SARIMA model
    forecasted_sales = sarima_results.get_forecast(steps=s)
    last_date = sales.index.max()
    next_year = last_date.year + 1

    # Create a new DataFrame for the forecasted sales
    forecasted_df = pd.DataFrame({'Mois': pd.date_range(start=last_date + DateOffset(months=1), periods=s, freq='M'),
                                  'Ventes': forecasted_sales.predicted_mean.values})

    st.subheader("Ventes Prévues")
    show_dataframe_fdf = forecasted_df.copy()
    show_dataframe_fdf['Mois'] = show_dataframe_fdf['Mois'].dt.strftime('%B %Y')
    show_dataframe_fdf['Ventes'] = show_dataframe_fdf['Ventes'].astype(float)  # Ensure the 'Ventes' column has a specific data type
    st.dataframe(show_dataframe_fdf)

    # Create a combined DataFrame with both real and forecasted sales
    combined_df = pd.concat([sales_df, forecasted_df])
    combined_df['Mois'] = combined_df['Mois'].dt.date
    combined_df = combined_df.reset_index(drop=True)
    
    # Calculate the figure size based on the number of data points
    num_data_points = len(sales_df) + len(forecasted_df)
    fig_width = len(sales_df) / 1.5  # Adjust the minimum width as needed

    # Create a chart with a dynamic figure size
    fig, ax = plt.subplots(figsize=(fig_width, fig_width / 4))

    ax.set_xlabel('Mois')
    ax.set_ylabel('Nombre de pièces commandées')
    ax.set_title(f"Prévision de l'année {next_year}")

    combined_len = len(combined_df)

    ax.set_xticks(range(combined_len))
    ax.set_xticklabels(combined_df['Mois'], rotation=45, ha='right')
    
    ax.bar(range(combined_len - s), combined_df['Ventes'][:combined_len - s], label='Demandes Réelles', alpha=0.7, color='blue')
    ax.bar(range(combined_len - s, combined_len), combined_df['Ventes'][combined_len - s:], label='Demandes Prévues', alpha=0.7, color='green')
    ax.plot(range(combined_len - s, combined_len), combined_df['Ventes'][combined_len - s:], linestyle='--', marker='o', color='red')
    ax.legend()

    # Draw vertical lines at each period based on the value of 's'
    for i in range(0, len(combined_df), s):
        ax.axvline(x=i, color='gray', linestyle='--')

    st.pyplot(fig)
