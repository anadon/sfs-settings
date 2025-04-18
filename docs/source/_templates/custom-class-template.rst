{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. automodule:: {{ fullname }}
   :members:
   :undoc-members:
   :show-inheritance:
   :imported-members:

   {% block modules %}
   {% if modules %}
   .. rubric:: Submodules

   .. autosummary::
      :toctree:
      :recursive:
      {% for item in modules %}
      {{ item }}
      {%- endfor %}
   {% endif %}
   {% endblock %}

.. autoclass:: {{ objname }}
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __call__
