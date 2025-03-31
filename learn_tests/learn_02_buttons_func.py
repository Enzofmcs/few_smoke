import flet as ft


# Creating a page with 3 items of the shop: Tobacco, Cigars, and Rolling Papers
# I want a invisible button that appears when the  mouse is over the item
# I want to add a button that will add the item to the cart when clicked
# I want to add a button that will remove the item from the cart when clicked
# I want to show how much items were added to the cart for each item

def main(page):
    # Adding images for the items
    tobacco_image = ft.Image(src="tobacco.png", width=100, height=100)
    cigars_image = ft.Image(src="cigars.png", width=100, height=100)
    rolling_papers_image = ft.Image(src="rolling_papers.png", width=100, height=100)

    # Adding the images to a Row
    page.add(
        ft.Row(
            controls=[
                tobacco_image,
                cigars_image, 
                rolling_papers_image,
            ]
        )
    )
        

ft.app(main)