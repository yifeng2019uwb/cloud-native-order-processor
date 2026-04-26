package main

import (
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {
		sa, err := setupServiceAccount(ctx)
		if err != nil {
			return err
		}

		if err = setupRegistry(ctx, sa); err != nil {
			return err
		}

		regions := make(pulumi.StringArray, len(clusters))
		for i, c := range clusters {
			if err = deployCluster(ctx, sa, c); err != nil {
				return err
			}
			regions[i] = pulumi.String(c.Region)
		}

		ctx.Export("clusterRegions", regions)
		return nil
	})
}
