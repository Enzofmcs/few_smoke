import flet as ft

# Creating a page with 3 items of the shop: Tobacco, Cigars, and Rolling Papers
# I want a invisible button that appears when the  mouse is over the item
# I want to add a button that will add the item to the cart when clicked
# I want to add a button that will remove the item from the cart when clicked
# I want to show how much items were added to the cart for each item




#1. create a page with 1 item of the shop 
#2. create a button that will add the item to the cart when clicked
#3. create a button that will remove the item from the cart when clicked

def main(page: ft.Page):
    cart = {}
    tobacco = ft.Image(src="tobacco.png", width=150, height=150)
    cigars = ft.Image(src="cigars.png", width=150, height=150)
    rolling_papers = ft.Image(src="rolling_papers.png", width=150, height=150)
        

    def item_container(shop_item):
        hov_state = False

        add_button = ft.ElevatedButton(
            content = ft.Icon(name=ft.Icons.ADD, color="green"),
            width=50,
            height=50,
            on_click=lambda e: add_to_cart(shop_item.src.split(".")[0]),
            visible=False,
        )
        remove_button = ft.ElevatedButton(content=ft.Icon(name=ft.Icons.REMOVE, color="red"), width=50, height=50, visible=False, on_click=lambda e: remove_from_cart(shop_item.src.split(".")[0]))

        def on_hov(e: ft.HoverEvent):
            nonlocal hov_state
            if hov_state == True:
                hov_state = False
                add_button.visible = False
                remove_button.visible = False
            else:
                hov_state = True
                print("hovering")
                add_button.visible = True
                remove_button.visible = True
            e.control.update()
            page.update()

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[add_button, remove_button], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                shop_item,
                ft.Text(f"Total: {cart.get(shop_item.src.split('.')[0], 0)}", color="black"),
                ft.Text(shop_item.src.split(".")[0], color="black"),
            ],
                
            alignment=ft.MainAxisAlignment.CENTER,  # Center vertically
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
            on_hover=on_hov,
        )
    def add_to_cart(item_name):
        cart[item_name] = cart.get(item_name, 0) + 1
        print(f"Added {item_name} to cart. Total: {cart[item_name]}")

    def remove_from_cart(item_name):
        if item_name in cart and cart[item_name] > 0:
            cart[item_name] -= 1
            print(f"Removed {item_name} from cart. Total: {cart[item_name]}")

    row = ft.Row(
        wrap=True,
        spacing=10,
        run_spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            item_container(tobacco),
            item_container(cigars),
            item_container(rolling_papers),
            item_container(rolling_papers),
            item_container(rolling_papers),
            item_container(rolling_papers),
            item_container(rolling_papers),
            ],
        width=page.width,
        height=page.height,
        scroll=ft.ScrollMode.AUTO,
    )

    page.add(
        ft.Container(
            ft.Column([
                row,
            ],),
            alignment=ft.alignment.center,
            adaptive=True,
            padding=10,
            margin=10,
            border=ft.border.all(1),
        )
        
        
    )


ft.app(main, assets_dir="assets")
