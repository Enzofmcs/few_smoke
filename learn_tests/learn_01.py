import flet as ft


# Defining the main function
def main(page: ft.Page):

    # Setting the title of the page
    page.title = "Hello few_smoke"

    # flet text control
    text = ft.Text(value="Few_smoke", color="red", size=30)

    # appending the text control to the page and updating the page
    page.add(text)


    # Adding a button to the page (no action defined yet)
    page.add(
        ft.Row(controls=[
        ft.TextField(label="Your name"),
        ft.ElevatedButton(text="Say my name!")
    ])
)
    
    page.add(
        ft.Row(controls=[
            ft.Text("A"),
            ft.Text("B"),
            ft.Text("C")
        ])
    )

    

ft.app(target=main)