{
  description = "Define development dependencies.";


  inputs = {
    # Which Nix upstream package branch to track
    nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  # What results we're going to expose
  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        packages = with pkgs; [
          python39Full
          python310Full
          python311Full
          python312Full
          python313Full
          python3Packages.distlib
          python3Packages.cython
          python3Packages.setuptools
          python3Packages.setuptoolsBuildHook
          python3Packages.wheel
          python3Packages.keyring
          (poetry.override { python3 = pkgs.python3; })
          direnv
          ruff
        ];
        # Declare what packages we need as a record. The use as a record is
        # needed because, without it, the data contained within can't be
        # referenced in other parts of this file.
        pythonldlibpath = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.stdenv.cc.cc.lib.outPath}/lib:${pkgs.lib.makeLibraryPath packages}:$NIX_LD_LIBRARY_PATH";
      in
        {
          devShells.default = pkgs.mkShell {
            inherit packages;
            # Getting the library paths needed for Python to be put into
            # LD_LIBRARY_PATH

          shellHook = ''
              export LD_LIBRARY_PATH="${pythonldlibpath}"
            '';
          };
        }
    );
}
