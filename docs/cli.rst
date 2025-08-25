CLI
===

List components and strategies
------------------------------

.. code-block:: bash

   flowfoundry list

Run a workflow from YAML
------------------------

.. code-block:: bash

   flowfoundry run examples/rag_local.yaml --state '{"query":"Hello!"}'

Write the workflow JSON Schema
------------------------------

.. code-block:: bash

   flowfoundry schema schema.json

Serve local API
---------------

.. code-block:: bash

   flowfoundry serve
