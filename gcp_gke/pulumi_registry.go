package main

import (
	"github.com/pulumi/pulumi-gcp/sdk/v9/go/gcp/artifactregistry"
	"github.com/pulumi/pulumi-gcp/sdk/v9/go/gcp/projects"
	"github.com/pulumi/pulumi-gcp/sdk/v9/go/gcp/serviceaccount"
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func setupRegistry(ctx *pulumi.Context, sa *serviceaccount.Account) error {
	// Artifact Registry repository — us-west1 matches the GKE cluster zone
	_, err := artifactregistry.NewRepository(ctx, "order-processor-registry", &artifactregistry.RepositoryArgs{
		RepositoryId: pulumi.String(arRepository),
		Location:     pulumi.String(arRegion),
		Format:       pulumi.String("DOCKER"),
	})
	if err != nil {
		return err
	}

	// Grant node SA pull access to Artifact Registry
	_, err = projects.NewIAMMember(ctx, "sa-ar-reader", &projects.IAMMemberArgs{
		Project: pulumi.String(projectID),
		Role:    pulumi.String("roles/artifactregistry.reader"),
		Member:  pulumi.Sprintf("serviceAccount:%s", sa.Email),
	})
	if err != nil {
		return err
	}

	return nil
}
