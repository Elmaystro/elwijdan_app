import streamlit as st
import numpy as np
import pandas as pd
from ortools.graph.python import min_cost_flow
import xlsxwriter
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data


# Function to load data and perform optimization
def optimize_delivery_time(orders_df, batch_df):
    # Check if demand equals supply
    total_demand = np.sum(orders_df['quantite'])
    total_supply = np.sum(batch_df['quantité'])

    if total_supply > total_demand:
        #st.warning("The supply > The demand. The problem is unbalanced.")
        new_row = {'n_commande': 'fective', 'quantite': total_supply-total_demand, 'temps_de_livraison':0}
        # Convert the new row to a DataFrame
        new_row_df = pd.DataFrame([new_row])
        # Concatenate the original DataFrame and the new row
        orders_df = pd.concat([orders_df, new_row_df], ignore_index=True)
    
    if total_supply < total_demand:
        #st.warning("The supply < The demand. The problem is unbalanced.")
        new_row = {'n_lot': 'lot a créer','date': pd.Timestamp.now(),'quantité': total_demand-total_supply }
        # Convert the new row to a DataFrame
        new_row_df = pd.DataFrame([new_row])
        # Concatenate the original DataFrame and the new row
        batch_df = pd.concat([batch_df, new_row_df], ignore_index=True)
        
    batch_df['date'] = pd.to_datetime(batch_df['date'])
    age_ = (pd.Timestamp.now() - batch_df['date']).dt.days.to_numpy()
    print(age_)
    lead_time = orders_df['temps_de_livraison'].to_numpy()
    cost = age_[:, np.newaxis] + lead_time
    # The number of batches and orders
    num_batches = len(batch_df)
    num_orders = len(orders_df)
    # Creating start_nodes and end_nodes arrays
    start_nodes = np.array([i for i in range(num_batches) for _ in range(num_orders)])
    end_nodes = np.array([j for _ in range(num_batches) for j in range(num_batches, num_batches + num_orders)])

    capacities = np.full(len(start_nodes), 999)
    unit_costs = cost.flatten()
    supplies = np.concatenate((batch_df['quantité'], -orders_df['quantite']), axis=0)
        

    # Instantiate a SimpleMinCostFlow solver.
    smcf = min_cost_flow.SimpleMinCostFlow()

    all_arcs = smcf.add_arcs_with_capacity_and_unit_cost(
        start_nodes, end_nodes, capacities, unit_costs
    )
    # Add supply for each node.
    smcf.set_nodes_supplies(np.arange(0, len(supplies)), supplies)
    status = smcf.solve()

    if status != smcf.OPTIMAL:
        st.error("There was an issue with the min cost flow input.")
        st.error(f"Status: {status}")
    else:
        st.success("Optimisation terminée avec succès !")

        # Extract the flow values for the solution
        flow = [smcf.flow(i) for i in all_arcs]

        # Create a result DataFrame with 'order_n_commande', 'batch_n_lot', and 'quantity'
        result_df = pd.DataFrame({
            'No commande': [orders_df['n_commande'].iloc[x - num_batches] for x in end_nodes],
            'No lot': [batch_df['n_lot'].iloc[x] for x in start_nodes],
            'Quantité': flow
        })
        print(smcf.optimal_cost())
        return smcf, result_df

# Upload Batch List
st.header("Télécharger la liste des lot")
batch_file = st.file_uploader("Télécharger la liste des lot", type=["xls", "xlsx"])

# Upload Orders List
st.header("Télécharger la liste des commandes")
orders_file = st.file_uploader("Télécharger la liste des commandes", type=["xls", "xlsx"])


if batch_file is not None and orders_file is not None:
    batch_df = pd.read_excel(batch_file, engine="openpyxl")  # Use "openpyxl" as the engine for Excel files.
    st.subheader("La list des lots")
    st.dataframe(batch_df)

    orders_df = pd.read_excel(orders_file, engine="openpyxl")  # Use "openpyxl" as the engine for Excel files.
    st.subheader("la liste des commandes")
    st.dataframe(orders_df)
    show_solution = st.button("Créer Le Plan Optimal")
    if show_solution:
    # Display the solution when the button is clicked
        model, result_df = optimize_delivery_time(orders_df, batch_df)
        if result_df is not None:
            result_df = result_df[result_df['Quantité'] != 0]
            st.subheader("Solution de Livraison Optimisée")
            # Access the cost values directly from the unit_costs array
            # Calculate the 'La date prévue de mise en rayon' column
            # Create the 'La date prévue de mise en rayon' column by mapping 'n_commande' to 'temps_de_livraison' in 'orders_df'
            result_df['La date prévue de mise en rayon'] = pd.Timestamp.now() + pd.to_timedelta(result_df['No commande'].map(orders_df.set_index('n_commande')['temps_de_livraison']), unit='D')
            result_df['La date prévue de mise en rayon'] = result_df['La date prévue de mise en rayon'].dt.date
            st.dataframe(result_df[result_df['No commande'] != 'fective'])
            st.download_button(
                label='📥 Télécharger le plan',
                data=to_excel(result_df[result_df['No commande'] != 'fective']),
                file_name="Plan.xlsx",
                mime="application/vnd.ms-excel"
            )