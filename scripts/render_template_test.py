import os
import sys
from types import SimpleNamespace

# Ensure project root is on sys.path so Django can import the project package
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xplorehub.settings')
import django
from django.template import loader, Context, TemplateSyntaxError


def main():
    django.setup()
    template_name = 'dashboards/admin_dashboard.html'
    try:
        tpl = loader.get_template(template_name)
        ctx = {
            'total_students': 10,
            'total_teachers': 3,
            'total_courses': 5,
            'recent_users': [],
            'user': SimpleNamespace(is_authenticated=False, username=''),
            'messages': [],
        }
        rendered = tpl.render(ctx)
        print('TEMPLATE_RENDER_OK')
    except TemplateSyntaxError as e:
        print('TEMPLATE_SYNTAX_ERROR:', e)
    except Exception:
        import traceback
        print('TEMPLATE_RENDER_EXCEPTION:')
        traceback.print_exc()


if __name__ == '__main__':
    main()
