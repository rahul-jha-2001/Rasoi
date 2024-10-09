import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(os.path.dirname(os.curdir))
import uuid
import logging
from concurrent import futures
import grpc
import django,os
from django.core.exceptions import ValidationError
from django.db import transaction

from dotenv import load_dotenv

load_dotenv()



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Product.settings')
django.setup()


from apiv1.models import Category,Product
from proto import Category_pb2,Product_pb2
from proto import Category_pb2_grpc,Product_pb2_grpc


logger = logging.getLogger(__name__)

class ProductService(Product_pb2_grpc.ProductServiceServicer):

    def _product_to_response(self,product:Product) -> Product_pb2.ProductResponse:

        response = Product_pb2.ProductResponse(
            Success = True,
            ProductUuid = str(product.ProductUuid) or "",
            Name = product.Name or "",
            IsAvailable = product.IsAvailable,
            Price = product.Price,
            CategoryUuid = str(product.category.CategoryUuid),
            Description = product.Description or "",
            ImageUrl = product.ImageUrl
        )
        return response
    
    @transaction.atomic
    def CreateProduct(self, request, context):
        try:
            category = Category.objects.get(CategoryUuid = request.CategoryUuid)
        except Category.DoesNotExist:
                logger.error(f"Category does not exist")
                context.abort(grpc.StatusCode.NOT_FOUND,"Category Not found")
        try:
            product = Product.objects.create(
                StoreUuid = request.StoreUuid,
                Name = request.Name,
                IsAvailable = request.IsAvailable,
                Price = request.Price,
                category = category,
                Description = request.Description,
                ImageUrl = request.ImageUrl
                )
            logger.info(f"Created Product: {product.ProductUuid}")
            return self._product_to_response(product)
       
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
       
        except Exception as e:
            logger.error(f"Error creating Product: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")
    def GetProduct(self, request, context):
        try:
            product = Product.objects.get(StoreUuid = request.StoreUuid,ProductUuid = request.ProductUuid)
            return self._product_to_response(product=product)
        
        except Product.DoesNotExist:
            logger.error(f"Product Does Not Exists")
            context.abort(grpc.StatusCode.NOT_FOUND,f"Product Does not Exists for product Id {request.ProductUuid} and StoreId {request.StoreUuid} ")
        
        except Exception as e:
            logger.error(f"Error getting Product: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")
    
    def ListProducts(self, request, context):
        try:
            products = Product.objects.filter(StoreUuid = request.StoreUuid)
            response = Product_pb2.ListProductsResponse()
            print(products)
            for product in products:
                
                product_response = self._product_to_response(product)
                response.products.append(product_response)
            return response    

        except Exception as e:
            logger.error(f"Error listing Products: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")
    
    @transaction.atomic
    def UpdateProduct(self, request, context):
        ProductUuid = request.ProductUuid
        try:
            product = Product.objects.get(ProductUuid = ProductUuid)
        except Product.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND,f"Product Does not Exist for Uuid {ProductUuid}")
        try:
            if request.HasField('Name'):
                    product.Name = request.Name
            
            if request.HasField('Description'):
                product.Description = request.Description
            
            if request.HasField('IsAvailable'):
                product.IsAvailable = request.IsAvailable

            if request.HasField('Price'):
                product.Price = request.Price
            
            if request.HasField('ImageUrl'):
                product.ImageUrl = request.ImageUrl
                        
            
            if request.HasField('CategoryUuid'):
                if request.CategoryUuid:
                    category = Category.objects.get(
                        CategoryUuid=request.CategoryUuid
                    )
                    product.category = category
                else:
                    product.category = None

            product.full_clean()
            product.save()

            logger.info(f"Updated category: {product.ProductUuid}")
            return self._product_to_response(product)        

        except ValidationError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"Error updating Product: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")

    def DeleteProduct(self, request, context):
        try:
            product = Product.objects.get(ProductUuid=request.ProductUuid)
            product.delete()
            
            logger.info(f"Deleted product: {request.ProductUuid}")
            return Product_pb2.DeleteProductResponse(Success=True)

        except Product.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "product not found")
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")



            


class CategoryService(Category_pb2_grpc.CategoryServiceServicer):
    
    def _category_to_response(self,category: Category) -> Category_pb2.CategoryResponse:

        response = Category_pb2.CategoryResponse(
            Success = True,
            CategoryUuid = str(category.CategoryUuid),
            Name = category.Name,
            Description = category.Description or ""
        )
        if category.Parent:
            response.ParentCategoryUuid = str(category.Parent.CategoryUuid)
        return response
    
    
    @transaction.atomic
    def CreateCategory(self, request, context):
        try:
            parent_category = None
            if request.ParentCategoryUuid:
                try:
                    parent_category = Category.objects.get(
                        CategoryUuid = request.ParentCategoryUuid
                    )
                except Category.DoesNotExist:
                    context.abort(grpc.StatusCode.NOT_FOUND,"Parent Category Not found")    
            category = Category.objects.create(
                    StoreUuid=request.StoreUuid,
                    Name=request.Name,
                    Description=request.Description,
                    Parent=parent_category
                )
            
            logger.info(f"Created category: {category.CategoryUuid}")
            return self._category_to_response(category)

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")
    def GetCategory(self, request, context):
        try:
            category = Category.objects.get(CategoryUuid = request.CategoryUuid)
            return self._category_to_response(category)
        except Category.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Category not found")
        except Exception as e:
            logger.error(f"Error getting category: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")

    @transaction.atomic
    def UpdateCategory(self, request, context):
        try:
            category = Category.objects.get(CategoryUuid=request.CategoryUuid)
            
            if request.HasField('Name'):
                category.Name = request.Name
            if request.HasField('Description'):
                category.Description = request.Description
            if request.HasField('ParentCategoryUuid'):
                if request.ParentCategoryUuid:
                    parent_category = Category.objects.get(
                        CategoryUuid=request.ParentCategoryUuid
                    )
                    category.Parent = parent_category
                else:
                    category.Parent = None

            category.full_clean()
            category.save()
            
            logger.info(f"Updated category: {category.CategoryUuid}")
            return self._category_to_response(category)

        except Category.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Category not found")
        except ValidationError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")

    def DeleteCategory(self, request, context):
        try:
            category = Category.objects.get(CategoryUuid=request.CategoryUuid)
            category.delete()
            
            logger.info(f"Deleted category: {request.CategoryUuid}")
            return Category_pb2.DeleteCategoryResponse(Success=True)

        except Category.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Category not found")
        except Exception as e:
            logger.error(f"Error deleting category: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")

    def ListCategories(self, request, context):
        try:
            categories = Category.objects.filter(StoreUuid=request.StoreUuid)
            response = Category_pb2.ListCategoriesResponse()
            
            for category in categories:
                category_response = self._category_to_response(category)
                response.categories.append(category_response)
            
            return response

        except Exception as e:
            logger.error(f"Error listing categories: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal server error")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add your services to the server
    Category_pb2_grpc.add_CategoryServiceServicer_to_server(CategoryService(), server)
    Product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    
    # Get the port from environment variables
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')
    
    # Bind the server to the specified port
    server.add_insecure_port(f'[::]:{grpc_port}')
    server.start()
    
    logger.info(f"gRPC server is running on port {grpc_port}")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()