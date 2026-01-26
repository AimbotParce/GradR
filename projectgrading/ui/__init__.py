from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, Static, ContentSwitcher, DataTable
from textual.containers import Horizontal, Vertical

class GradingApp(App):
    CSS = """
    #sidebar { width: 30; background: $panel; border-right: thin $primary; }
    #main-content { width: 1fr; }
    """

    async def on_mount(self) -> None:
        # 1. Setup Database Connection here
        # 2. Populate the Sidebar Tree
        tree = self.query_one(Tree)
        root = tree.root
        root.expand()
        
        # Example logic: Fetch subjects from DB
        # subjects = await get_subjects()
        subject_node = root.add("Mathematics", expand=True)
        subject_node.add_leaf("Classroom A")
        subject_node.add_leaf("Classroom B")

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Tree("Subjects", id="sidebar")
            with Vertical(id="main-content"):
                with ContentSwitcher(initial="dashboard"):
                    yield Static("Select a classroom to begin", id="dashboard")
                    yield StudentManager(id="student_view")
                    yield ProjectManager(id="project_view")
                    # ... other views
        yield Footer()

    async def on_tree_node_selected(self, event: Tree.NodeSelected):
        # Logic to switch views based on what was clicked
        if event.node.allow_expand: # It's a subject
            pass 
        else: # It's a classroom
            self.query_one(ContentSwitcher).current = "student_view"