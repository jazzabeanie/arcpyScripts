redistributePolygon Documentation
=================================

[//]: # (An early version of this tool is in O:\Data\Planning_IP\Admin\Staff\Jared\Sewer Strategy Report Catchments\UpperRoss\redistributePolygon.py)

[//]: # (Current version is in jj_methods.py)

Description
-----------

This tool spatially redistributes the data from one polygon to another. It was
originally developed for the purpose of finding the growth model projections
for pump station catchments of Southern Suburbs.

Usage
-----

Before using this tool, the Issues section below should be fully understood.

To use this tool, import the jj_methods module into your python script with:

`import jj_methods as jj`  

or

`jj = imp.load_source('jj_methods', r'\\corp\tcc\Plan & Comm Engage\Plan\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\jj_methods.py')`

Call the redistributePolygon method, passing in a dictionary with the required
parameters.

`jj.redistributePolygon(redistribution_inputs_dictionary)`


Parameters
----------

The redistributePolygon method takes 1 argument - a dictionary containing all
the required layers.

The dictionary must contain the following keys:
    - layer_to_redistribute_to
    - layer_to_be_redistributed
    - output_filename
    - distribution_method
    - fields_to_be_distributed
    - properties_layer (optional)

### layer_to_redistribute_to

The value of this key should contain the path to the polygons to which the data
will be redistributed.  It should not contain overlapping polygons. This use
case has not been considered.

### layer_to_be_redistributed

The value of this key should contain the path to the polygons which contains
the data to be redistributed. It should not contain overlapping polygons. This
use case has not been considered.

### output_filename

The value of this key should contain the path to the location to save the
results. If it exists, it will be deleted.

### distribution_method

The value of this key tell the tool how to distribute the data. It can contain
an integer (referring to a defined method), or it can contain a features layer.
Each case is explained below.

#### 1

If the value of the distribution_method key is 1, the distribution will be
performed based on the portion of area.

![An example of distribution method 1\label{distribution_method_1}](.\distribution_method_1.PNG)

In the example demonstrated by Figure \ref{distribution_method_1}; 

- polygon 1 will receive 50% of the data from polygon 2;
- polygon 3 will receive 50% of the data polygon 2, and 50% of the data polygon 4; and
- the remaining 50% of polygon 4 will not be included in the output.

#### 2

If the value of the distribution_method key is 2, the distribution will be
performed based on the portion of lots.

![An example of distribution method 2\label{distribution_method_2}](.\distribution_method_2.PNG)

In the example demonstrated by Figure \ref{distribution_method_2};

- polygon 1 will receive 33% of the data from polygon 2; and
- polygon 3 will receive 67% of the data from polygon 1, and 100% of the data from polygon 4.

#### feature layer

If the value of the distribution_method key contains the path to a polygon, the data will be distributed based on the amount of overlapping area of each polygon.

![An example of the feature layer distribution method\label{distribution_method_string}](.\distribution_method_string.PNG)

In the example demonstrated by Figure \ref{distribution_method_string}, where the net developable area is passed in as the distribution method;

- polygon 1 will receive 33% of the data from polygon 2;
- polygon 3 will receive 67% of the data from polygon 2; and
- the data from polygon 4 will not be included in the output.

### fields_to_be_distributed

The value of this key should contain a list of the field names that contain the data to be distributed.

### properties_layer (optional)

By default, where the properties layer is required, this tool will use the `sde_vector.TCC.Cadastral\sde_vector.TCC.Land_Parcels` layer. If a different properties layer is required, it can be provided here.

Although this parameter was intended to provide the ability to distribute based on a historical properties layer, any layer can be used as the properties layer and the distribution will be based on the number of polygons whose centroid falls within each area.

For example, if the layers in Figure \ref{distribution_method_string} were used in the tool, but the net developable area was used as the properties layer and a distribution method of 2 was selected, we would get the following results:

- polygon 1 will receive no data (the distribution only looks at the centroid of the properties layer)
- polygon 3 will receive 100% of the data from polygon 2 
- polygon 3 will also receive 50% of the data from polygon 4 (the tool will distribute by area for a given polygon of the layer_to_be_distributed when no properties can be found)
- 50% of the data from polygon 4 will not be included in the output

Issues
------

This tool has been tested against various scenarios and the issues below have been identified. In addition to these, unknown issues may also exist.

### Double counting issue

I don't think this is still an issue. TODO: write a unit test to confirm.

There is an issue with properties that cross pump station catchments being
counted twice. This issue seems to affects only the proportion allocated, not
the total population across the catchments. The error is negligible in the
typical catchment where the number of properties is high and the number of
properties crossing the boundaries is low in comparison. It does become an
issue when the inverse is true, especially when the few properties in the
catchments contain a high number of EP (eg, JCU, the Hospital, Lavarack
Barracks).

### Rounding errors

For integer fields, rounding errors of up to 1 can be found for each area that intersects a unique combination of layer_to_redistribute_to and layer_to_be_redistributed. For field that allow higher precision (such as float, and double), this round error doesn't exist. TODO: create a unit test that confirms this.

### Empty lots

This tool should be used with caution when operating under the assumption that properties equate to non-vacant dwellings. The tool has no way of distinguishing between habitable, inhabitable, vacant, and non-vacant dwellings, and vacant properties. Because it just looks at the portion of these properties, if there is an error it will over assign a data to one polygon, and under assign it to another. In this case, the total will not be affected.

### High EP concentration over few properties

The tool assumes that population and employment EPs are evenly distributed
across a catchment. In areas where EPs are concentrated over a few
properties, it can calculate a concentrated population as being spread
over several pump station catchments.

### Intermitent data issue
The intersecting_polygons layer can have growth model data joined to it
multiple times. for example, you will find POP_2016_2017, and POP_2021_2022
fields. This doesn't seem to impact on the final results, but this issue
should be fully understood before and / or fixed before this tool is used on
other areas.

Quality Control (Unit Tests)
----------------------------

Unit tests have been written to aid development and demonstrate functionality of the tool. The tests are run through the jj_tests.py file.

TODO: write unit tests provided for the examples given in this documentation.
