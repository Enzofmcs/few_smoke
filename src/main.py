import flet as ft
import platform

class ShopItem:
    def __init__(self, name, image_src, width=150, height=150):
        self.name = name
        self.image_src = image_src
        self.image = ft.Image(src=image_src, width=width, height=height)
        self.quantity_in_cart = 0
        self.quantity_text = ft.Text(f"Total: {self.quantity_in_cart}", color="black")
        self.name_text = ft.Text(self.name, color="black")

class ShopView:
    def __init__(self, page):
        self.page = page
        self.items = [
            ShopItem("tobacco", "tobacco.png"),
            ShopItem("cigars", "cigars.png"),
            ShopItem("rolling_papers", "rolling_papers.png")
        ]
        self.cart = {}
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI of the application"""
        item_containers = [self.create_item_container(item) for item in self.items]
        
        row = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=item_containers,
            width=self.page.width,
            height=self.page.height,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.page.add(
                ft.Container(
                    ft.Container(
                        content=ft.Image("logo.png", width=200, height=200),
                        alignment=ft.alignment.top_left,

                    ),
                    adaptive=True,
                    height=220,
                    margin=10,
                    border_radius=10,
                    bgcolor=ft.colors.BLUE_100,
                ),
                ft.Container(
                    ft.Column([row]),
                    alignment=ft.alignment.center,
                    adaptive=True,
                    padding=10,
                    margin=10,
                )
        )
    
    def create_item_container(self, item):
        """Create a container for a shop item with hover functionality"""
        add_button = ft.ElevatedButton(
            content=ft.Icon(name=ft.icons.ADD, color="green"),
            width=50,
            height=50,
            on_click=lambda e, item=item: self.add_to_cart(item),
            visible=False,
        )
        
        remove_button = ft.ElevatedButton(
            content=ft.Icon(name=ft.icons.REMOVE, color="red"),
            width=50,
            height=50,
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
                        controls=[add_button, remove_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    item.image,
                    item.quantity_text,
                    item.name_text,
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
            bgcolor=ft.colors.BLUE_50,
            border_radius=5,
            on_hover=lambda e, item=item: self.handle_hover(e, item),
        )
        
        return container
    
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
        item.quantity_in_cart += 1
        self.cart[item.name] = item.quantity_in_cart
        item.quantity_text.value = f"Total: {item.quantity_in_cart}"
        print(f"Added {item.name} to cart. Total: {item.quantity_in_cart}")
        print(self.cart)
        self.page.update()
    
    def remove_from_cart(self, item):
        """Remove an item from the cart"""
        if item.quantity_in_cart > 0:
            item.quantity_in_cart -= 1
            self.cart[item.name] = item.quantity_in_cart
            item.quantity_text.value = f"Total: {item.quantity_in_cart}"
            print(f"Removed {item.name} from cart. Total: {item.quantity_in_cart}")
            print(self.cart)
            self.page.update()

def main(page: ft.Page):
    # Create the shop view

    # Desktop settings
    page.window.title_bar_hidden = True
    page.window.frameless = False
    page.window.full_screen = True
    
    # Create the shop view with platform-specific settings
    shop_view = ShopView(page)

# Run the application
ft.app(main, assets_dir="assets")