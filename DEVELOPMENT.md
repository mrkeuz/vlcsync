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
    
### Roadmap:

- [x] Add portable `*.exe` build for Windows
- [ ] Add ability to set static addresses i.e. for remote sync (for support external pc)
- [ ] Add offsets controlling (web api for cross-platform) for fix unsync video/audio
- [ ] Automatic tune vlc [config](https://wiki.videolan.org/Preferences/#:~:text=Configuration%20File&text=Windows%3A%20%25appdata%25%5Cvlc%5C,%5CApplication%20Data%5Cvlc%5Cvlcrc) file for correct expose
