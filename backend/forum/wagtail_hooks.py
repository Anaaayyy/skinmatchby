from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel
from .models import ForumCategory

class ForumCategoryViewSet(SnippetViewSet):
    model = ForumCategory
    menu_label = 'Категории форума'
    menu_icon = 'folder-open-inverse'
    menu_order = 100
    list_display = ['name', 'slug', 'icon', 'order', 'created_at']
    search_fields = ['name', 'slug', 'description']
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description'),
        FieldPanel('icon'),
        FieldPanel('order'),
    ]

register_snippet(ForumCategoryViewSet)