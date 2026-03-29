import customtkinter as ctk
from auth_window import AuthWindow
from loading_screen import LoadingScreen


def main():
    def on_auth_success():
        from gui import DeliveryApp

        root = ctk.CTk()
        root.withdraw()

        loading = LoadingScreen(root, "Starting NetLogo engine...")

        def finish_loading():
            loading.finish()
            root.destroy()

            app = DeliveryApp()
            app.withdraw()

            def show_maximized():
                app.state("zoomed")
                app.deiconify()
                app.lift()
                app.focus_force()

            app.after(50, show_maximized)
            app.mainloop()

        root.after(2000, finish_loading)
        root.mainloop()

    auth = AuthWindow(on_success_callback=on_auth_success)
    auth.mainloop()


if __name__ == "__main__":
    main()