# AUTOGENERATED! DO NOT EDIT! File to edit: 00_base.ipynb (unless otherwise specified).

__all__ = ['Base_Object', 'Base_Handler']

# Cell

class Base_Object(object):
    '''
    A base object. The only requirement of all
    objects is that they have an object_id which can be used
    as a DataFrame index and for tracking in the Handler class.
    '''

    _object_id = None

    def __init__(self, object_id=None):
        '''
        args:
            object_id: (any) all objects must have an id. all object_ids
                are cast to a str for consistency
        '''
        if object_id:
            self._object_id = str(object_id)
        else:
            raise ValueError('custom object class must have ' \
                             'an object_id')

    @property
    def object_id(self):
        return self._object_id

    @object_id.setter
    def object_id(self, new_id):
        self._object_id = str(new_id)

    def __repr__(self):
        return self._object_id

    def get_properties(self):
        '''
        This method casts all defined attributes that are a property
        type to a dictionary that can be used by the handler to create
        a Pandas DataFrame from the objects
        '''
        prop_dict = vars(self)
        prop_dict = {k[1:]: v for k, v in prop_dict.items()}
        props = [n for n in dir(self) if isinstance(getattr(self.__class__, n), property)]
        prop_dict = {k: v for k, v in prop_dict.items() if k in props}
        return prop_dict

# Cell

import pandas as pd
import inspect
from .base import Base_Object

class Base_Handler():
    def __init__(self, obj_class=Base_Object, obj_list=None, obj_df=None, property_mappings={}):
        '''
        class should be instantiated with a list of Team object created using
        this package or with a pandas dataframe with the appropriate colums

        args:
            obj_class (custom_class): the class that will be used to build the df.
                the df will be built using properties from each object
            obj_list (list of instantiated obj classes): list of objects to use
            obj_df  (DataFrame): alternatively, the objects can be built from a dataframe
            property_mappings (dict): dictionary mapping property names to column names.
                by default the names will be the same. If loading data through a DataFrame
                the columns should be renmed to match the property or the appropriate
                mapping must be defined.
        '''

        # get a property list from the base object
        self._obj_class = obj_class
        self._obj_properties = list(obj_class(object_id='test').get_properties().keys())
        self._property_mappings = property_mappings

        if 'object_id' not in self._obj_properties:
            raise ValueError('provided object class is missing an object_id property')

        # unless mappings specified, infer from df or from property list
        if not self._property_mappings:
            # assign
            if obj_df is not None:
                self._property_mappings = {col: col for col in obj_df.columns}
            else:
                self._property_mappings = {x: x for x in self._obj_properties}

        # column mappings are just a reverse translation of property mappings
        self._column_mappings = {v: k for k, v
                                 in self._property_mappings.items()}

        # check that property mapping matches with base object properties
        if not set(self._property_mappings.keys()).issubset(self._obj_properties):
            raise ValueError('Unknown property in mapping make sure the following ' \
                f'keys are in the mapping: \n{self._obj_properties}')

        # validate inputs
        if obj_list is not None and obj_df is not None:
            raise NotImplementedError('please provide either team_list or ' \
            'team_df and not both')

        elif obj_list is not None:

            e = TypeError('obj_list must be a list of the specified obj_class')

            if type(obj_list)!=list:
                raise e
            try:
                self._objects = dict(
                    zip(
                        [obj.object_id for obj in obj_list],
                        obj_list
                    )
                )

                self.update_df_from_objects()
            except AttributeError:
                raise e

        elif obj_df is not None:
            if not isinstance(obj_df, type(pd.DataFrame())):
                raise ValueError('team_df should be a pandas dataframe')

            if not set(self._property_mappings.values()).issubset(obj_df.columns):
                raise ValueError('DataFrame columns do not match the property ' \
                    'mapping values and cannot be mapped')

            self.dataframe = obj_df.reset_index().copy()
            self.update_objects_from_df()

    @property
    def object_properties(self):
        return self._obj_properties

    @property
    def objects(self):
        '''
        a dictionary of the objects labeled by object_id
        '''
        return self._objects

    def __repr__(self):
        return repr(self.dataframe.set_index('object_id'))

    def update_objects_from_df(self):
        '''
        function to refresh Base_Handler.objects based on DataFrame
        Changes can be made at the dataframe level and applied back to the
        Objects.
        '''
        self._objects = {
            row[self._property_mappings['object_id']]:
            self._obj_class(
                **{self._column_mappings[k]: v
                for k, v in row.to_dict().items()
                if self._column_mappings.get(k) in self._obj_properties}
            )
            for _, row in self.dataframe.iterrows()
        }

    def update_df_from_objects(self):
        '''
        function to refresh DataFrame based on Base_Handler.objects.
        Changes can be made at the object level and applied back to the
        DataFrame
        '''
        self.dataframe = pd.DataFrame(data={
            col: [eval(f'o.{prop}') for o in self._objects.values()]
            for prop, col in self._property_mappings.items()
        })

    def query(self, query, as_type='handler'):
        '''
        returns a df that matches the supplied query with
        the objects in the objects column.

        args:
            query: (str) str query that will be applied to dataframe
                object through Pandas.DataFrame.query() method
            as_type: (str) how queried objects are returned.
                    - 'handler': returns new handler instance with queried
                            subset of objects.
                    - 'dataframe': returns the queried DataFrame with associated
                            objects in the 'objects' column.ValueError
                    - 'objects': returns only the objects from the query as a
                            Pandas series or just the single object if only one
                            is returned.
        '''

        df = self.dataframe.query(query).copy()
        objects = df['object_id'].map(self._objects.get)

        if as_type=='handler':
            new_handler = self.__class__(
                obj_list=objects.to_list(),
                property_mappings=self._property_mappings
                )
            return new_handler
        elif as_type=='dataframe':
            df['object'] = objects
            return df

        elif as_type=='objects':
            return objects.squeeze()

        else:
            raise ValueError(f'{as_type} not a valid for as_type argument')




    def map_object_method(self, col_name, obj_method):

        '''
        built to function similarly to DataFrame.map. This method will map
        a method from the object class across all rows of the dataframe.
        complex methods can be built at the object level and applied to the
        dataset using this method.

        args:
            col_name (str): column name to be mapped to
            obj_method (method): the method from the base object to apply
        '''

        if not inspect.isfunction(obj_method):
            raise TypeError(f'{obj_method.__qualname__} is not a method')

        if self._obj_class.__name__!=obj_method.__qualname__.split('.')[0]:
            raise TypeError(f'{obj_method.__qualname__} is not a method ' \
                            f'of {self._obj_class}')

        method_name = obj_method.__name__
        data = {k: eval(f'v.{method_name}()')
                for k, v in self._objects.items()}

        self.dataframe.set_index('object_id', inplace=True)
        self.dataframe[col_name] = pd.Series(data=data, index=data.keys())
        self.dataframe.reset_index(inplace=True)