# Development

### Build and install
  ```shell
  pip3 install -U .
  ```

### Build on windows 
  ```
  ./build_win.sh
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
    
### Roadmap:

- [x] Add portable `*.exe` build for Windows
- [ ] Add offsets controlling (web api for cross-platform) for fix unsync video/audio


