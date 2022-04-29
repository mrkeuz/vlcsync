# Development

### Build and install
  ```shell
  pip3 install -U .
  ```
  
### Publish
  - Prepare  
     ```shell
    poetry config repositories.testpypi https://test.pypi.org/legacy/
    poetry config pypi-token.testpypi <TOKEN>
    
    poetry config repositories.pypi https://upload.pypi.org/legacy/
    poetry config pypi-token.pypi <TOKEN>
    ```  
  
  - Publish
    ```shell
    poetry publish --build -r testpypi
    
    poetry publish --build -r pypi
    ````