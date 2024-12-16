# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: Product.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'Product.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rProduct.proto\x12\x07product\"\x98\x01\n\x14\x43reateProductRequest\x12\x11\n\tStoreUuid\x18\x01 \x01(\t\x12\x0c\n\x04Name\x18\x02 \x01(\t\x12\x13\n\x0bIsAvailable\x18\x03 \x01(\x08\x12\r\n\x05Price\x18\x04 \x01(\x02\x12\x14\n\x0c\x43\x61tegoryUuid\x18\x05 \x01(\t\x12\x13\n\x0b\x44\x65scription\x18\x06 \x01(\t\x12\x10\n\x08ImageUrl\x18\x07 \x01(\t\";\n\x11GetProductRequest\x12\x13\n\x0bProductUuid\x18\x01 \x01(\t\x12\x11\n\tStoreUuid\x18\x02 \x01(\t\"(\n\x13ListProductsRequest\x12\x11\n\tStoreUuid\x18\x01 \x01(\t\"+\n\x14\x44\x65leteProductRequest\x12\x13\n\x0bProductUuid\x18\x01 \x01(\t\"\x89\x02\n\x14UpdateProductRequest\x12\x13\n\x0bProductUuid\x18\x01 \x01(\t\x12\x11\n\x04Name\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x18\n\x0bIsAvailable\x18\x03 \x01(\x08H\x01\x88\x01\x01\x12\x12\n\x05Price\x18\x04 \x01(\x02H\x02\x88\x01\x01\x12\x19\n\x0c\x43\x61tegoryUuid\x18\x05 \x01(\tH\x03\x88\x01\x01\x12\x18\n\x0b\x44\x65scription\x18\x06 \x01(\tH\x04\x88\x01\x01\x12\x15\n\x08ImageUrl\x18\x07 \x01(\tH\x05\x88\x01\x01\x42\x07\n\x05_NameB\x0e\n\x0c_IsAvailableB\x08\n\x06_PriceB\x0f\n\r_CategoryUuidB\x0e\n\x0c_DescriptionB\x0b\n\t_ImageUrl\"\xa6\x01\n\x0fProductResponse\x12\x0f\n\x07Success\x18\x01 \x01(\x08\x12\x13\n\x0bProductUuid\x18\x02 \x01(\t\x12\x0c\n\x04Name\x18\x03 \x01(\t\x12\x13\n\x0bIsAvailable\x18\x04 \x01(\x08\x12\r\n\x05Price\x18\x05 \x01(\x02\x12\x14\n\x0c\x43\x61tegoryUuid\x18\x06 \x01(\t\x12\x13\n\x0b\x44\x65scription\x18\x07 \x01(\t\x12\x10\n\x08ImageUrl\x18\x08 \x01(\t\"(\n\x15\x44\x65leteProductResponse\x12\x0f\n\x07Success\x18\x01 \x01(\x08\"B\n\x14ListProductsResponse\x12*\n\x08products\x18\x01 \x03(\x0b\x32\x18.product.ProductResponse2\x85\x03\n\x0eProductService\x12H\n\rCreateProduct\x12\x1d.product.CreateProductRequest\x1a\x18.product.ProductResponse\x12\x42\n\nGetProduct\x12\x1a.product.GetProductRequest\x1a\x18.product.ProductResponse\x12H\n\rUpdateProduct\x12\x1d.product.UpdateProductRequest\x1a\x18.product.ProductResponse\x12N\n\rDeleteProduct\x12\x1d.product.DeleteProductRequest\x1a\x1e.product.DeleteProductResponse\x12K\n\x0cListProducts\x12\x1c.product.ListProductsRequest\x1a\x1d.product.ListProductsResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Product_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CREATEPRODUCTREQUEST']._serialized_start=27
  _globals['_CREATEPRODUCTREQUEST']._serialized_end=179
  _globals['_GETPRODUCTREQUEST']._serialized_start=181
  _globals['_GETPRODUCTREQUEST']._serialized_end=240
  _globals['_LISTPRODUCTSREQUEST']._serialized_start=242
  _globals['_LISTPRODUCTSREQUEST']._serialized_end=282
  _globals['_DELETEPRODUCTREQUEST']._serialized_start=284
  _globals['_DELETEPRODUCTREQUEST']._serialized_end=327
  _globals['_UPDATEPRODUCTREQUEST']._serialized_start=330
  _globals['_UPDATEPRODUCTREQUEST']._serialized_end=595
  _globals['_PRODUCTRESPONSE']._serialized_start=598
  _globals['_PRODUCTRESPONSE']._serialized_end=764
  _globals['_DELETEPRODUCTRESPONSE']._serialized_start=766
  _globals['_DELETEPRODUCTRESPONSE']._serialized_end=806
  _globals['_LISTPRODUCTSRESPONSE']._serialized_start=808
  _globals['_LISTPRODUCTSRESPONSE']._serialized_end=874
  _globals['_PRODUCTSERVICE']._serialized_start=877
  _globals['_PRODUCTSERVICE']._serialized_end=1266
# @@protoc_insertion_point(module_scope)