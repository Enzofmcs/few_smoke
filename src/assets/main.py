import flet as ft
from dataclasses import dataclass
import os
import shutil
import json
import numpy as np
import pandas as pd
import datetime


# ============ DATA MODELS ============

@dataclass
class ShopItem:
    """Model representing a shop item with cart functionality"""
    
    _next_id = 1

    @classmethod
    def get_next_id(cls):
        """Get the next available ID and increment the counter"""
        current_id = cls._next_id
        cls._next_id += 1
        return current_id
    
    def __init__(self, name, image_src, cost=0.0, price=0.0, width=120, height=120, stock_quantity=0):
        self.id = ShopItem.get_next_id()
        self.name = name
        self.image_src = image_src
        self.cost = cost
        self.price = price
        self.width = width
        self.height = height
        self.quantity_in_cart = 0
        self.stock_quantity = stock_quantity
        
        # Initialize UI components
        self.image = ft.Image(src=self.image_src, width=self.width, height=self.height)
        self.quantity_text = ft.Text(f"Carrinho: {self.quantity_in_cart}", color=ft.colors.BLACK)
        self.name_text = ft.Text(self.name, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD, size=20)
        self.stock_text = ft.Text(f"Estoque: {self.stock_quantity}", color=ft.colors.BLACK)
        # These will be set later in the Shop class
        self.add_button = None
        self.remove_button = None
    
    def to_dict(self):
        """Convert the ShopItem to a dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'image_src': self.image_src,
            'cost': self.cost,
            'price': self.price,
            'stock_quantity': self.stock_quantity
        }


# ============ CONTROLLERS ============


class Shop:
    """Controller for shop functionality and UI"""
    def __init__(self, page):
        self.page = page
        
        df_items = pd.read_excel(os.path.join(os.getcwd(), 'src/assets/estoque.xlsx'))
        df_sells = pd.read_excel(os.path.join(os.getcwd(), 'src/assets/vendas.xlsx'))



        # Convert DataFrame to list of dictionaries
        items_data = df_items.to_dict('records')

        # Create ShopItem objects from the Excel data
        self.items = [ShopItem(
            item.get("name", ""),  
            item.get("image_src", ""), 
            item.get("cost", 0.0), 
            item.get("price", 0.0), 
            item.get("width", 120), 
            item.get("height", 120), 
            item.get('stock_quantity', 0)
        ) for item in items_data]

        self.cart = {}

        self.sell = max(df_sells['Id_venda']) if not df_sells.empty else 0

    def update_item_excel(self, item_id, updated_data):
        """
        Update item information in the Excel file
        
        Args:
            item_id: The ID of the item to update
            updated_data: Dictionary containing the fields to update (e.g., {'name': 'New Name'})
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        file_path = os.path.join(os.getcwd(), 'src/assets/estoque.xlsx')
        
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Find the row with the matching ID
            row_index = df.index[df['id'] == item_id].tolist()
            
            if not row_index:
                print(f"No item found with ID {item_id}")
                return False
            
            # Update the fields in the dataframe
            for key, value in updated_data.items():
                if key in df.columns:
                    df.at[row_index[0], key] = value
            
            # Save the updated dataframe back to Excel
            df.to_excel(file_path, index=False)
            
            # Also update the item in memory
            for item in self.items:
                if item.id == item_id:
                    for key, value in updated_data.items():
                        if hasattr(item, key):
                            setattr(item, key, value)
                        # Special case for updating display text
                        if key == 'name':
                            item.name_text.value = value
                    break
            
            print(f"Successfully updated item with ID {item_id}")
            return True
        
        except Exception as e:
            print(f"Error updating item: {e}")
            return False

    def export_sell(self, cart_items, payment):
        file_path = os.path.join(os.getcwd(), 'src/assets/vendas.xlsx')
        df = pd.read_excel(file_path)
        current_time = datetime.datetime.now()
        
        for item in cart_items:
            new_row = {
                'Id_venda': self.sell + 1,
                'Id_produto': item.id,
                'Produto': item.name,
                'Quantidade': item.quantity_in_cart,
                'Custo': item.cost,
                'Preço': item.price,
                'Pagamento': payment,
                'Data/Hora': current_time  
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        self.sell += 1  # Increment the sell counter
        df.to_excel(file_path, index=False)
    
    def build_ui(self):
        """Build the main UI of the shop"""
        sorted_items = sorted(self.items, key=lambda item: item.name)
    
        item_containers = [self.create_item_container(item) for item in sorted_items]
        
        row = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=item_containers,
            width=self.page.width,
            height=self.page.height,
        )
        
        return [
            create_header(self.page),
            ft.Container(
                ft.Column([row]),
                alignment=ft.alignment.center,
                adaptive=True,
                padding=10,
                margin=10,
                border_radius=10,
                bgcolor=ft.colors.WHITE,
            )
        ]
    
    def reset_stock_quantity(self):
        """Set the stock_quantity of all items to 0"""
        for item in self.items:
            item.stock_quantity = 0
    
    def create_item_container(self, item):
        """Create a container for a shop item with hover functionality"""
        add_button = ft.ElevatedButton(
            content=ft.Icon(name=ft.icons.ADD_ROUNDED, color=ft.colors.GREEN),
            adaptive=True,
            on_click=lambda e, item=item: self.add_to_cart(item),
            visible=False,
        )
        
        remove_button = ft.ElevatedButton(
            content=ft.Icon(name=ft.icons.REMOVE_ROUNDED, color=ft.colors.RED),
            adaptive=True,
            on_click=lambda e, item=item: self.remove_from_cart(item),
            visible=False,
        )
        
        # Store buttons in the item for later access
        item.add_button = add_button
        item.remove_button = remove_button
        
        container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[add_button, remove_button],
                        
                    ),
                    item.name_text,
                    ft.Row([
                        item.quantity_text,
                        item.stock_text,

                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    
                    item.image,
                    
                    
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            width=250,
            height=250,
            padding=10,
            margin=10,
            bgcolor=ft.colors.BLACK12,
            border_radius=5,
            on_hover=lambda e, item=item: self.handle_hover(e, item),
        )

        
        
        return container
    

    def add_shop_excel(self, item):
        
        # Create file path
        file_path = os.path.join(os.getcwd(), 'src/assets/estoque.xlsx')

        df = pd.read_excel (file_path)

        df = pd.concat([df, pd.DataFrame([item])], ignore_index=True)

        # Save the updated DataFrame back to Excel
        df.to_excel(file_path, index=False)

        
        print(f"Excel file created: {file_path}")

    def remove_shop_excel(self, item):

        df = pd.read_excel(os.path.join(os.getcwd(), 'src/assets/estoque.xlsx'))

        df = df[df["id"] != item.id]
        
        # Save the updated DataFrame back to Excel
        df.to_excel(os.path.join(os.getcwd(), 'src/assets/estoque.xlsx'), index=False)
    



    
    def handle_hover(self, e, item):
        """Handle hover events for item containers"""
        if e.data == "true":  # Mouse entered
            item.add_button.visible = True
            item.remove_button.visible = True
        else:  # Mouse exited
            item.add_button.visible = False
            item.remove_button.visible = False
        
        e.control.update()
    
    def add_to_cart(self, item):
        """Add an item to the cart"""
        if item.stock_quantity > item.quantity_in_cart:
            if item.id in self.cart:
                self.cart[item.id].quantity_in_cart += 1
            else:
                # Make a copy of the item for the cart
                item.quantity_in_cart = 1
                self.cart[item.id] = item
                
            item.quantity_text.value = f"Carrinho: {item.quantity_in_cart}"
            print(f"Added {item.name} to cart. Total: {item.quantity_in_cart}")
            self.print_cart()
            self.page.update()

    def delete_from_cart(self, item):
        if item.id in self.cart:
            del self.cart[item.id]
    
    def remove_from_cart(self, item):
        """Remove an item from the cart"""
        if item.quantity_in_cart > 0:
            item.quantity_in_cart -= 1
            
            if item.quantity_in_cart == 0:
                # If quantity is zero, remove from cart
                self.delete_from_cart(item)
            else:
                # Update the item in cart
                self.cart[item.id] = item
                
            item.quantity_text.value = f"Carrinho: {item.quantity_in_cart}"
            print(f"Removed {item.name} from cart. Total: {item.quantity_in_cart}")
            self.print_cart()
            self.page.update()
    
    def get_cart_items(self):
        """Get all items that are in the cart"""
        return list(self.cart.values())
    
    def get_items(self):
        """Get all items in the shop"""
        return self.items
    
    def get_items_dictionary(self):
        return {item.id: item.to_dict() for item in self.items}
    
    def get_items_json(self):
        """Get all items in JSON format"""
        return json.dumps([item.to_dict() for item in self.items], indent=4)
    
    def print_cart(self):
        """Print the contents of the cart for debugging"""
        if not self.cart:
            print("Cart is empty")
            return
        
        print("Current Cart Contents:")
        print("-" * 40)
        
        total_cost = 0
        for item_id, item in self.cart.items():
            item_total = item.quantity_in_cart * item.price
            total_cost += item_total
            
            print(f"ID: {item.id}, Name: {item.name}")
            print(f"Quantity: {item.quantity_in_cart}, Price: ${"{:,.2f}".format(item.price).replace(".", ",")}, Total: ${item_total:.2f}")
            print("-" * 30)
        
        print(f"Total Cart Value: ${total_cost:.2f}")
        print("-" * 40)

# ============ UI COMPONENTS ============

def create_header(page):
    """Create the header navigation component"""
    return ft.Container(
        content=ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            width=page.window.width,
            controls=[
                ft.Container(
                    content=ft.Image("logo.png", width=80, height=80),
                    adaptive=True,
                    ink=True,
                    on_click=lambda e: page.go("/"),
                    margin=10,
                ),
                ft.Container(
                    content=ft.Text("Home", text_align=ft.TextAlign.CENTER, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                    margin=10,
                    padding=10,
                    bgcolor=ft.colors.ORANGE,
                    adaptive=True,
                    border_radius=10,
                    ink=True,
                    on_click=lambda e: page.go("/"),
                ),
                ft.Container(
                    content=ft.Text("Cadastrar novos itens", text_align=ft.TextAlign.CENTER, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                    margin=10,
                    padding=10,
                    bgcolor=ft.colors.ORANGE,
                    adaptive=True,
                    border_radius=10,
                    ink=True,
                    on_click=lambda e: page.go("/editor"),
                ),
                ft.Container(
                    content=ft.Text("Carrinho", text_align=ft.TextAlign.CENTER, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                    margin=10,
                    padding=10,
                    bgcolor=ft.colors.ORANGE,
                    adaptive=True,
                    border_radius=10,
                    ink=True,
                    on_click=lambda e: page.go("/cart"),
                ),
            ],
        ),
        adaptive=True,
        height=100,
        border_radius=5,
        bgcolor=ft.colors.BLACK87,
        width=page.window.width,
        alignment=ft.alignment.center,
    )




# ============ VIEWS ============

def home_view(page, shop):
    """Home page view showing all shop items"""
    return ft.View(
        route="/",
        scroll=ft.ScrollMode.AUTO,
        controls=shop.build_ui(),
    )

def cart_view(page, shop):
    """Cart view showing selected items"""
    cart_items = shop.get_cart_items()

    

    def buy():
        """Handle checkout process"""
        if not cart_items:
            page.snack_bar = ft.SnackBar(content=ft.Text("Your cart is empty"))
            page.snack_bar.open = True
            page.update()
            return
        
        if cg.value is not None:
            shop.export_sell(cart_items, cg.value)
            
            for item in cart_items:
                item.stock_quantity -= item.quantity_in_cart
                item.quantity_text = ft.Text(f"Carrinho: {item.quantity_in_cart}", color=ft.colors.BLACK)
                item.quantity_in_cart = 0
                item.quantity_text.value = "Total: 0"

            shop.update_item_excel(item.id, {'stock_quantity' : item.stock_quantity})
            

            
            
            shop.cart.clear()
            page.go("/")

    
    if not cart_items:
        content = ft.Column(
            [
                create_header(page),
                ft.Container(
                    ft.Text("Your cart is empty", color=ft.colors.BLACK, size=20),
                    alignment=ft.alignment.center,
                    margin=20,
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                )
            ],
            alignment=ft.MainAxisAlignment.START
        )
    else:
        items_list = ft.Column(
            [
                ft.ListTile(
                    leading=item.image,
                    title=ft.Text(item.name, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),

                    subtitle=ft.Text(f"Quantidade: {item.quantity_in_cart}      Valor: R${"{:,.2f}".format(item.price).replace(".", ",")}", color=ft.colors.BLACK),
                )
                for item in cart_items
            ],
            spacing=10,
        )


        
        checkout_button = ft.ElevatedButton(
                text="Proceed to Checkout",
                on_click=lambda e: buy(),
                bgcolor=ft.colors.GREEN,
        )

        cg = ft.RadioGroup(
            content=ft.Row(
                    [
                        ft.Radio(value="pix", label="Pix", fill_color=ft.colors.BLACK, hover_color=ft.colors.BLACK, label_style= ft.TextStyle(color=ft.colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.Radio(value="credito", label="Crédito", fill_color=ft.colors.BLACK, hover_color=ft.colors.BLACK, label_style= ft.TextStyle(color=ft.colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.Radio(value="debito", label="Débito", fill_color=ft.colors.BLACK, hover_color=ft.colors.BLACK, label_style= ft.TextStyle(color=ft.colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.Radio(value="dinheiro", label="Dinheiro", fill_color=ft.colors.BLACK, hover_color=ft.colors.BLACK,label_style= ft.TextStyle(color=ft.colors.BLACK, weight=ft.FontWeight.BOLD)),
                    ]
                )
        )
        
        content = ft.Column(
            [
                create_header(page),
                ft.Container(
                    ft.Column([
                        ft.Text("Your Cart", color=ft.colors.BLACK, size=24, weight=ft.FontWeight.BOLD),
                        items_list,
                        ft.Divider(height=1, color=ft.colors.BLACK),
                        ft.Column(
                            controls=[

                                ft.Text(f"Total: R${"{:,.2f}".format(sum(item.price * item.quantity_in_cart for item in cart_items)).replace(".", ",")}", color=ft.colors.BLACK, size=20, weight=ft.FontWeight.BOLD),
                                ft.Divider(height=1, color=ft.colors.BLACK),
                                cg,

                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        checkout_button,
                    ]),
                    padding=20,
                    margin=20,
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                )
            ],
            alignment=ft.MainAxisAlignment.START
        )
    
    return ft.View(
        route="/cart",
        scroll=ft.ScrollMode.AUTO,
        controls=[content],
    )

def editor_view(page, shop):
    """Product editor view for adding new products"""



    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            # Get the selected file
            selected_file = e.files[0]
            source_path = selected_file.path  # Full path of the selected file
            destination_folder = os.path.join(os.getcwd(), "src/assets/images")  # Path to the assets folder
            destination_path = os.path.join(destination_folder, selected_file.name)  # Full path in assets

            # Ensure the assets folder exists
            os.makedirs(destination_folder, exist_ok=True)

            # Move the file to the assets folder
            shutil.move(source_path, destination_path)

            # Update the UI to show the new file path
            image_field.value = f"{selected_file.name}"
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    
    # Form fields
    name_field = ft.TextField(label="Product Name", color=ft.colors.BLACK, width=200)
    image_field = ft.TextField(label="Selected Image", read_only=True, color=ft.colors.BLACK, width=200)
    price_field = ft.TextField(label="Price", color=ft.colors.BLACK, width=200)
    cost_field = ft.TextField(label="Cost", color=ft.colors.BLACK, width=200)
    stock_quantity_field = ft.TextField(label="Stock Quantity", color=ft.colors.BLACK, width=200)

    select_image_button = ft.ElevatedButton(
        "Select Image",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg"],
            allow_multiple=False
        )
    )
    
    def add_product(e):
        # Validate required fields
        if not all([name_field.value, image_field.value, price_field.value, 
                    cost_field.value, stock_quantity_field.value]):
            page.snack_bar = ft.SnackBar(content=ft.Text("Please fill all fields"))
            page.snack_bar.open = True
            page.update()
            return
            
        # Validate numeric fields
        try:
            cost = float(cost_field.value)
            price = float(price_field.value)
            stock = int(stock_quantity_field.value)
            
            if price < 0 or cost < 0 or stock < 0:
                raise ValueError("Values cannot be negative")
                
        except ValueError:
            page.snack_bar = ft.SnackBar(content=ft.Text("Please enter valid numbers"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Create the item
        new_item = ShopItem(name_field.value, image_field.value, cost=float(cost_field.value), price=float(price_field.value), stock_quantity=int(stock_quantity_field.value))
        shop.items.append(new_item)
        name_field.value = ""
        image_field.value = ""
        cost_field.value = ""
        price_field.value = ""
        stock_quantity_field.value = ""
        shop.add_shop_excel(new_item.to_dict())
        page.update()
        page.go("/")
        page.go("/editor")
            


    def container_item(item):

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(src=item.image_src, width=80, height=80),
                    ft.Column(
                        controls=[
                            ft.Text(item.name, color=ft.colors.BLACK, size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Price: {item.price}", color=ft.colors.BLACK),
                            ft.Text(f"Cost: {item.cost}", color=ft.colors.BLACK),
                            ft.Text(f"Stock Quantity: {item.stock_quantity}", color=ft.colors.BLACK),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    ft.Column(
                        controls=[
                            ft.ElevatedButton(
                                content=ft.Icon(name=ft.icons.DELETE, color=ft.colors.RED),
                                on_click=lambda e: remove_product(e, item),
                                bgcolor=ft.colors.WHITE,
                                adaptive=True,
                            ),
                        

                        ]
                    )

                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            ink=True,
            alignment=ft.alignment.center,
            width=320,
            height=150,
            padding=10,
            margin=10,
            bgcolor=ft.colors.BLACK12,
            border_radius=5,
        )

    def remove_product(e, item):
        shop.delete_from_cart(item)
        shop.items.remove(item)
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Removed {name_field.value} from the shop!"))
        page.snack_bar.open = True
        name_field.value = ""
        image_field.value = ""
        shop.remove_shop_excel(item)
        page.update()
        page.go("/")
        page.go("/editor")
    
    return ft.View(
        route="/editor",
        scroll=ft.ScrollMode.AUTO,
        controls=[
            create_header(page),
            ft.Container(
                ft.Column([
                    ft.Text("Adicionar produto", color=ft.colors.BLACK, size=24, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        wrap=True,
                        spacing=10,
                        controls = [
                        name_field,
                        price_field,
                        cost_field,
                        stock_quantity_field,
                        select_image_button,
                        ]
                    ),
                    ft.ElevatedButton(
                        text="Add Product",
                        on_click=add_product,
                        bgcolor=ft.colors.ORANGE,
                        color=ft.colors.BLACK,
                    ),
                    
                    ft.Text("Lista de Produtos", color=ft.colors.BLACK, size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        run_spacing=10,
                        wrap=True,
                        controls=[
                            container_item(item) for item in sorted(shop.get_items(), key=lambda item: item.name)
                        ]
                    )
                ]),
                adaptive=True,
                alignment=ft.alignment.center,
                padding=20,
                margin=20,
                bgcolor=ft.colors.WHITE,
                border_radius=10,
            )
        ],
    )


# ============ MAIN APP ============

def main(page: ft.Page):
    """Main entry point for the Flet application"""
    # Setup page properties
    page.title = "Poco Fumo"
    page.bgcolor = ft.colors.WHITE54
    page.window.title_bar_hidden = False
    page.window.frameless = False
    
    # Initialize the shop controller
    shop = Shop(page)
    
    # Define route handling
    def route_change(e):
        page.views.clear()
        route = e.route
        
        if route == "/":
            page.views.append(home_view(page, shop))
        elif route == "/cart":
            page.views.append(cart_view(page, shop))
        elif route == "/editor":
            page.views.append(editor_view(page, shop))
        
        page.update()
    
    # Setup routing
    page.on_route_change = route_change
    
    # Go to the initial route
    page.go(page.route)

# Run the application
if __name__ == "__main__":
    ft.app(main, assets_dir="images")