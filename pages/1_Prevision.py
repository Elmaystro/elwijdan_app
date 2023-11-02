import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pandas.tseries.offsets import DateOffset
from pmdarima import auto_arima

st.header("Téléchargez la liste des ventes")
sales_file = st.file_uploader("Téléchargez un fichier Excel pour la liste des commandes", type=["xls", "xlsx"])
s = st.slider("Les taille de la saison", 1, 24, 12)

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

# Fit an ARIMA model using auto_arima
if calculate_button and sales_file is not None:
    sales = sales_df.copy()
    data = sales_df.copy()
    sales['Mois'] = pd.to_datetime(sales['Mois'])
    data['Mois'] = pd.to_datetime(sales['Mois'])
    data.set_index('Mois', inplace=True)
    data['Ventes'] = data['Ventes'].astype(float)  # Ensure the 'Ventes' column has a specific data type

    auto_model = auto_arima(data, seasonal=True, m=s)  # Adjust 'm' for the seasonality of your data

    # Get the best model's order (p, d, q) and seasonal order (P, D, Q, m)
    order = auto_model.get_params()['order']
    seasonal_order = auto_model.get_params()['seasonal_order']

    # Adjust a SARIMA model to the data
    sarima_model = sm.tsa.SARIMAX(sales['Ventes'], order=order, seasonal_order=seasonal_order)
    sarima_results = sarima_model.fit()
    # Predict future sales using the SARIMA model
    forecasted_sales = sarima_results.get_forecast(steps=12)
    last_date = sales['Mois'].max()
    next_year = last_date.year + 1

    # Create a new DataFrame for the forecasted sales
    forecasted_df = pd.DataFrame({'Mois': pd.date_range(start=sales['Mois'].max() + DateOffset(months=1), periods=12, freq='M'),
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
    fig_width =len(sales_df)/1.5  # Adjust the minimum width as needed

    # Create a chart with a dynamic figure size
    #fig, ax = plt.subplots(figsize=(fig_width, 6))
    # Create a chart with a larger figure size
    fig, ax = plt.subplots(figsize=(fig_width,fig_width/4 ))

    ax.set_xlabel('Mois')
    ax.set_ylabel('Nombre de pièces commandées')
    ax.set_title(f"Prévision de l'année {next_year}")

    combined_len = len(combined_df)

    ax.set_xticks(range(combined_len))
    ax.set_xticklabels(combined_df['Mois'], rotation=45, ha='right')

    ax.bar(range(combined_len - 12), combined_df['Ventes'][:combined_len - 12], label='Demandes Réelles', alpha=0.7, color='blue')
    ax.bar(range(combined_len - 12, combined_len), combined_df['Ventes'][combined_len - 12:], label='Demandes Prévues', alpha=0.7, color='green')
    ax.plot(range(combined_len - 12, combined_len), combined_df['Ventes'][combined_len - 12:], linestyle='--', marker='o', color='red')
    ax.legend()

    st.pyplot(fig)
