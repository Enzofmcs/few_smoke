import pandas as pd
import os


# Define the columns we want in our Excel file
columns = ['Id_venda', 'Id_produto', 'Produto', 'Quantidade', 'Preço', 'Custo', 'Pagamento', 'Data/Hora']

# Create an empty DataFrame with these columns
df = pd.DataFrame(columns=columns)

excel_path = os.path.join(os.getcwd(), 'src/assets/vendas.xlsx')

# Save the DataFrame to an Excel file
df.to_excel(excel_path, index=False)